import { Route, Routes } from "react-router-dom";

import { TodayPage } from "./pages/TodayPage";
import { ProfilePage } from "./pages/ProfilePage";
import { WeightPage } from "./pages/WeightPage";
import { GoalsPage } from "./pages/GoalsPage";
import { MealsPage } from "./pages/MealsPage";
import { ExercisePage } from "./pages/ExercisePage";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { RemindersPage } from "./pages/RemindersPage";
import { LoginPage } from "./pages/LoginPage";
import { AuthProvider } from "./features/auth/AuthContext";
import { RequireAuth } from "./features/auth/RequireAuth";

export function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<RequireAuth />}>
          <Route path="/" element={<TodayPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/weight" element={<WeightPage />} />
          <Route path="/goals" element={<GoalsPage />} />
          <Route path="/meals" element={<MealsPage />} />
          <Route path="/exercise" element={<ExercisePage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/reminders" element={<RemindersPage />} />
          <Route path="*" element={<TodayPage />} />
        </Route>
      </Routes>
    </AuthProvider>
  );
}
