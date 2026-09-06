import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { AnalyticsPage } from "./AnalyticsPage";
const data={period:"7d",weight:{measurement_count:1,latest_kg:70,change_kg:null},nutrition:{totals:{calories_kcal:100,protein_g:2},nutrition_missing_item_count:1},exercise:{session_count:1,total_duration_minutes:30,distance_km:2,calories_burned_kcal:0}};
describe("AnalyticsPage",()=>{it("loads, shows data, and switches period",async()=>{const fetchMock=vi.fn(()=>Promise.resolve({ok:true,json:()=>Promise.resolve(data)}));vi.stubGlobal("fetch",fetchMock);render(<BrowserRouter><AnalyticsPage/></BrowserRouter>);expect(await screen.findByText("Latest: 70 kg")).toBeInTheDocument();expect(screen.getByText(/missing nutrition/)).toBeInTheDocument();await userEvent.setup().selectOptions(screen.getByLabelText("Period"),"30d");expect(fetchMock).toHaveBeenCalled();});it("shows API error",async()=>{vi.stubGlobal("fetch",vi.fn(()=>Promise.resolve({ok:false})));render(<BrowserRouter><AnalyticsPage/></BrowserRouter>);expect(await screen.findByRole("alert")).toBeInTheDocument();});});
