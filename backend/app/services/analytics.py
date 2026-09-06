from datetime import datetime, time, timezone, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.models.weight import WeightRecord
from app.models.meal import Meal
from app.models.exercise import ExerciseSession
from app.repositories.profile import ProfileRepository
from app.repositories.user import UserRepository
from app.schemas.analytics import AnalyticsResponse

class AnalyticsService:
    def __init__(self, db: Session): self.db=db; self.users=UserRepository(db); self.profiles=ProfileRepository(db)
    def get(self, period: str, now: datetime | None=None) -> AnalyticsResponse:
        if period not in {'7d','30d'}: raise ValueError('Unsupported period.')
        user=self.users.get_or_create_local_user(); profile=self.profiles.get_profile(); tz=profile.timezone if profile and profile.timezone else 'UTC'; zone=ZoneInfo(tz)
        local_now=(now or datetime.now(timezone.utc)).astimezone(zone); end=local_now.date(); start=end-timedelta(days=int(period[:-1])-1)
        begin=datetime.combine(start,time.min,tzinfo=zone).astimezone(timezone.utc); finish=datetime.combine(end+timedelta(days=1),time.min,tzinfo=zone).astimezone(timezone.utc)
        weights=list(self.db.scalars(select(WeightRecord).where(WeightRecord.user_id==user.id,WeightRecord.recorded_at>=begin,WeightRecord.recorded_at<finish).order_by(WeightRecord.recorded_at)))
        meals=list(self.db.scalars(select(Meal).options(selectinload(Meal.items)).where(Meal.user_id==user.id,Meal.eaten_at>=begin,Meal.eaten_at<finish)))
        exercises=list(self.db.scalars(select(ExerciseSession).where(ExerciseSession.user_id==user.id,ExerciseSession.performed_at>=begin,ExerciseSession.performed_at<finish)))
        dates=[start+timedelta(days=i) for i in range((end-start).days+1)]
        latest_by_day={}
        for w in weights: latest_by_day[w.recorded_at.astimezone(zone).date()]=w
        weight_values=[Decimal(str(w.weight_kg)) for w in weights]
        meal_by_day={d:[] for d in dates}
        for m in meals: meal_by_day[m.eaten_at.astimezone(zone).date()].append(m)
        nutrition=[]; item_count=known_items=0
        for d in dates:
            items=[i for m in meal_by_day[d] for i in m.items]; item_count+=len(items); known_items+=sum(any(getattr(i,x) is not None for x in ('calories_kcal','protein_g','carbohydrates_g','fat_g')) for i in items)
            total=lambda f: float(sum((Decimal(str(getattr(i,f))) for i in items if getattr(i,f) is not None),Decimal('0')))
            nutrition.append({'date':d,'meal_count':len(meal_by_day[d]),'calories_kcal':total('calories_kcal'),'protein_g':total('protein_g'),'carbohydrates_g':total('carbohydrates_g'),'fat_g':total('fat_g')})
        ex_by_day={d:[] for d in dates}
        for e in exercises: ex_by_day[e.performed_at.astimezone(zone).date()].append(e)
        exercise=[]
        for d in dates:
            es=ex_by_day[d]; sm=lambda f:float(sum((Decimal(str(getattr(e,f))) for e in es if getattr(e,f) is not None),Decimal('0')))
            exercise.append({'date':d,'session_count':len(es),'duration_minutes':sum(e.duration_minutes for e in es),'distance_km':sm('distance_km'),'calories_burned_kcal':sm('calories_burned_kcal')})
        activities={}
        for e in exercises:
            x=activities.setdefault(e.activity_type.value,{'session_count':0,'duration_minutes':0});x['session_count']+=1;x['duration_minutes']+=e.duration_minutes
        totals={k:sum(Decimal(str(x[k])) for x in nutrition) for k in ('calories_kcal','protein_g','carbohydrates_g','fat_g')}
        return AnalyticsResponse(period=period,timezone=tz,start_date=start,end_date=end,weight={'series':[{'date':d,'weight_kg':float(w.weight_kg)} for d,w in latest_by_day.items()],'measurement_count':len(weights),'first_kg':float(weight_values[0]) if weight_values else None,'latest_kg':float(weight_values[-1]) if weight_values else None,'min_kg':float(min(weight_values)) if weight_values else None,'max_kg':float(max(weight_values)) if weight_values else None,'average_kg':float(sum(weight_values)/len(weight_values)) if weight_values else None,'change_kg':float(weight_values[-1]-weight_values[0]) if len(weight_values)>1 else None},nutrition={'daily':nutrition,'meal_count':len(meals),'item_count':item_count,'items_with_any_nutrition':known_items,'nutrition_missing_item_count':item_count-known_items,'totals':{k:float(v) for k,v in totals.items()},'average_per_calendar_day':{k:float(v/len(dates)) for k,v in totals.items()}},exercise={'daily':exercise,'session_count':len(exercises),'total_duration_minutes':sum(e.duration_minutes for e in exercises),'average_duration_minutes':float(sum(e.duration_minutes for e in exercises)/len(exercises)) if exercises else None,'distance_km':float(sum((Decimal(str(e.distance_km)) for e in exercises if e.distance_km is not None),Decimal('0'))),'calories_burned_kcal':float(sum((Decimal(str(e.calories_burned_kcal)) for e in exercises if e.calories_burned_kcal is not None),Decimal('0'))),'activity_types':activities})
