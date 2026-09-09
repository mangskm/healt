import { useEffect, useState } from "react";

import { EmptyState, LoadingState, useToast } from "../components/UiProviders";
import { downloadExport, getMonthlyReport } from "../services/api";
import type { ExportDataType, ExportRange, MonthlyReport } from "../types/reports";

function shiftMonth(month: string, offset: number): string {
  const [year, monthNumber] = month.split("-").map(Number);
  const value = new Date(Date.UTC(year, monthNumber - 1 + offset, 1));
  return `${value.getUTCFullYear()}-${String(value.getUTCMonth() + 1).padStart(2, "0")}`;
}

function monthLabel(month: string): string {
  return new Intl.DateTimeFormat(undefined, { month: "long", year: "numeric", timeZone: "UTC" }).format(new Date(`${month}-01T12:00:00Z`));
}

function number(value: number | null): string {
  return value === null ? "Not available" : value.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

export function ReportsPage() {
  const [selectedMonth, setSelectedMonth] = useState<string | null>(null);
  const [report, setReport] = useState<MonthlyReport | null>(null);
  const [error, setError] = useState(false);
  const [exportType, setExportType] = useState<ExportDataType>("weight");
  const [exportRange, setExportRange] = useState<ExportRange>("month");
  const [customStart, setCustomStart] = useState("");
  const [customEnd, setCustomEnd] = useState("");
  const [exportError, setExportError] = useState(false);
  const [exporting, setExporting] = useState(false);
  const { success } = useToast();

  const load = () => {
    setReport(null);
    setError(false);
    void getMonthlyReport(selectedMonth ?? undefined).then((value) => {
      setReport(value);
      if (selectedMonth !== value.period.month) setSelectedMonth(value.period.month);
      setCustomStart(value.period.start_date);
      setCustomEnd(value.period.end_date);
    }).catch(() => setError(true));
  };

  useEffect(load, [selectedMonth]);

  const changeMonth = (offset: number) => {
    if (report) setSelectedMonth(shiftMonth(report.period.month, offset));
  };

  const exportData = async () => {
    setExportError(false);
    setExporting(true);
    try {
      await downloadExport(exportType, exportRange, report?.period.month, customStart || undefined, customEnd || undefined);
      success("Your CSV download is ready.");
    } catch {
      setExportError(true);
    } finally {
      setExporting(false);
    }
  };

  const weight = report?.weight;
  const nutrition = report?.nutrition;
  const exercise = report?.exercise;
  return <main className="page-shell reports-page">
    <header className="page-header"><div><p className="eyebrow">Personal records</p><h1>Reports</h1><p className="intro">A factual monthly view of the data you entered. Missing values are never estimated.</p></div></header>
    {!report && !error && <LoadingState label="Loading monthly report…" />}
    {error && <section className="alert alert-error" role="alert"><strong>Report could not be loaded.</strong><span>Try again without changing any of your tracking data.</span><button className="button button-secondary" type="button" onClick={load}>Retry</button></section>}
    {report && <>
      <section className="report-month-picker" aria-label="Select report month"><button className="button button-secondary" type="button" onClick={() => changeMonth(-1)}>Previous month</button><div><p className="eyebrow">Monthly summary</p><strong>{monthLabel(report.period.month)}</strong><span>{report.period.start_date} to {report.period.end_date} · {report.period.timezone}</span></div><button className="button button-secondary" type="button" onClick={() => changeMonth(1)}>Next month</button></section>
      <section className="content-grid report-summary" aria-label="Monthly summary">
        <article className="card"><p className="eyebrow">Weight</p><h2>Recorded measurements</h2>{weight && weight.measurement_count > 0 ? <dl className="report-details"><div><dt>Measurements</dt><dd>{weight.measurement_count}</dd></div><div><dt>First recorded</dt><dd>{number(weight.first)} {weight.unit}</dd></div><div><dt>Latest recorded</dt><dd>{number(weight.latest)} {weight.unit}</dd></div><div><dt>Recorded change</dt><dd>{weight.recorded_change === null ? "Not available" : `${number(weight.recorded_change)} ${weight.unit}`}</dd></div><div><dt>Range</dt><dd>{number(weight.minimum)}–{number(weight.maximum)} {weight.unit}</dd></div><div><dt>Average</dt><dd>{number(weight.average)} {weight.unit}</dd></div></dl> : <EmptyState title="No weight measurements recorded this month." />}</article>
        <article className="card"><p className="eyebrow">Nutrition entered</p><h2>Meal totals</h2>{nutrition && nutrition.item_count > 0 ? <><div className="metric-grid"><span><strong>{nutrition.totals.calories_kcal}</strong> kcal entered</span><span><strong>{nutrition.totals.protein_g}g</strong> protein</span><span><strong>{nutrition.totals.carbohydrates_g}g</strong> carbs</span><span><strong>{nutrition.totals.fat_g}g</strong> fat</span></div><p className="muted-note">{nutrition.meal_count} meals · {nutrition.item_count} meal items. {nutrition.nutrition_missing_item_count > 0 ? `${nutrition.nutrition_missing_item_count} item(s) have no nutrition entered.` : ""}</p></> : <EmptyState title={nutrition?.meal_count ? "No nutrition values entered this month." : "No meals recorded this month."} />}</article>
        <article className="card"><p className="eyebrow">Exercise</p><h2>Activity totals</h2>{exercise && exercise.session_count > 0 ? <><div className="metric-grid"><span><strong>{exercise.session_count}</strong> sessions</span><span><strong>{exercise.total_duration_minutes}</strong> min</span><span><strong>{exercise.distance}</strong> {exercise.distance_unit}</span><span><strong>{exercise.calories_burned_kcal}</strong> kcal entered</span></div>{exercise.activity_types.length > 0 && <ul className="compact-list activity-list">{exercise.activity_types.map((activity) => <li key={activity.activity_type}><strong>{activity.activity_type.replace("_", " ")}</strong><span>{activity.session_count} session(s) · {activity.duration_minutes} min</span></li>)}</ul>}</> : <EmptyState title="No exercise sessions recorded this month." />}</article>
        <article className="card"><p className="eyebrow">How to read this</p><h2>Direct records only</h2><p className="muted-note">Totals include only values you entered. A meal item with no nutrition stays missing, and days without a weight measurement are not filled in.</p><p className="muted-note">Exercise distance is shown in canonical kilometers because the Profile has no distance preference.</p></article>
      </section>
      <section className="card export-card"><div><p className="eyebrow">Export your data</p><h2>Download CSV</h2><p className="muted-note">CSV files use your Profile timezone and include only your own records. Text fields are made safe for spreadsheets.</p></div><div className="export-controls"><label>Data type<select aria-label="Export data type" value={exportType} onChange={(event) => setExportType(event.target.value as ExportDataType)}><option value="weight">Weight</option><option value="meals">Meals</option><option value="exercise">Exercise</option></select></label><label>Date range<select aria-label="Export date range" value={exportRange} onChange={(event) => setExportRange(event.target.value as ExportRange)}><option value="month">Selected month</option><option value="last_30_days">Last 30 days</option><option value="custom">Custom range</option></select></label>{exportRange === "custom" && <div className="custom-range"><label>Start date<input aria-label="Export start date" type="date" value={customStart} onChange={(event) => setCustomStart(event.target.value)} /></label><label>End date<input aria-label="Export end date" type="date" value={customEnd} onChange={(event) => setCustomEnd(event.target.value)} /></label></div>}<button className="button" type="button" disabled={exporting || (exportRange === "custom" && (!customStart || !customEnd))} onClick={() => void exportData()}>{exporting ? "Preparing CSV…" : "Download CSV"}</button></div>{exportError && <div className="alert alert-error" role="alert">CSV could not be prepared. Check the selected date range and try again.</div>}</section>
    </>}
  </main>;
}
