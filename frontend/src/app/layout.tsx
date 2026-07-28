import { Outlet } from "react-router-dom";
import { useState } from "react";
import CustomSidebar from "../components/common/custom_sidebar/CustomSidebar";


export default function Layout() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="flex h-screen">
      <CustomSidebar
        collapsed={collapsed}
        setCollapsed={setCollapsed}
      />

      <main className="flex-1 overflow-auto bg-slate-100">
        <Outlet />
      </main>
    </div>
  );
}