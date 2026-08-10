import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./layout";
import ReportsPage from "../components/ReportsPage";
import ReportsContent from "../components/reports/ReportsContent";
import Dashboard from "../components/page";
import AdminContent from "../components/admin/AdminContent";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          {/*<Route path="/" element={<Dashboard />} />
          <Route path="/reports" element={<Reports />} />*/}
          <Route path="/reports" element={<ReportsPage/>} />
          <Route path="/create-report" element={<ReportsContent/>}/>
          <Route path="/admin" element={<AdminContent/>}/>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}