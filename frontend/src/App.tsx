import { Route, Routes } from "react-router-dom";

import { TodayPage } from "./pages/TodayPage";
import { ProfilePage } from "./pages/ProfilePage";
import { WeightPage } from "./pages/WeightPage";
import { GoalsPage } from "./pages/GoalsPage";
import { MealsPage } from "./pages/MealsPage";
import { ExercisePage } from "./pages/ExercisePage";
import { AnalyticsPage } from "./pages/AnalyticsPage";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<TodayPage />} />
      <Route path="/profile" element={<ProfilePage />} />
      <Route path="/weight" element={<WeightPage />} />
      <Route path="/goals" element={<GoalsPage />} />
      <Route path="/meals" element={<MealsPage />} />
      <Route path="/exercise" element={<ExercisePage />} />
      <Route path="/analytics" element={<AnalyticsPage />} />
      <Route path="*" element={<TodayPage />} />
    </Routes>
  );
}
