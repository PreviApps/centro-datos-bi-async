import { NavLink, useNavigate } from "react-router-dom";
import clsx from "clsx";
import { LockFill } from "@gravity-ui/icons";
import logo from "../../../assets/logo-grupo-previsalud.webp";
import icon from "../../../assets/icono.webp";
import { Button, Tooltip } from "@heroui/react";

const menu = [
  {
    name: "Reportes",
    icon: "fa-file",
    route: "/reports",
  },
  {
    name: "Tableros",
    icon: "fa-users",
    route: "/boards",
    disabled: true
  },
];

export default function Sidebar({
  collapsed,
  setCollapsed,
}) {
  const navigate = useNavigate();
  return (
    <aside
      className={clsx(
        "bg-slate-900 text-white transition-all duration-300",
        collapsed ? "w-16" : "w-60"
      )}
    >
      <button
        className="p-4"
        onClick={() => setCollapsed(!collapsed)}
      >
        ☰
      </button>

      <div className="flex justify-center">
        <img
          src={collapsed ? icon : logo}
          alt="Grupo Previsalud"
          className={clsx(
            "object-contain transition-all duration-300",
            collapsed ? "h-10 w-10" : "h-14"
          )}
          onClick={()=> navigate("/")}
        />
      </div>

      <nav>
        {menu.map((item) => (
          item.disabled ? (
            <div
              key={item.route}
              className={clsx(
                "flex items-center gap-3 p-3 text-slate-400 cursor-not-allowed",
                collapsed && "justify-center"
              )}
            >
              <i className={`fa ${item.icon}`} />

              {!collapsed && (
                <Tooltip delay={0}>
                  <Tooltip.Trigger>
                    <span className="flex items-center gap-2">
                      {item.name}
                      <LockFill />
                    </span>
                  </Tooltip.Trigger>

                  <Tooltip.Content>
                    <p>Próximamente</p>
                  </Tooltip.Content>
                </Tooltip>
              )}
            </div>
          ) : (
            <NavLink
              key={item.route}
              to={item.route}
              className={({ isActive }) =>
                clsx(
                  "flex items-center gap-3 p-3 hover:bg-slate-700 text-white",
                  isActive && "bg-slate-800",
                  collapsed && "justify-center"
                )
              }
            >
              <i className={`fa ${item.icon}`} />

              {!collapsed && <span>{item.name}</span>}
            </NavLink>
          )
        ))}
      </nav>
    </aside>
  );
}