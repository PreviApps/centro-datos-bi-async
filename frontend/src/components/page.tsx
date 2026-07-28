// src/pages/Dashboard.jsx

export default function Dashboard() {
  return (
    <div className="p-8">
      <div className="rounded-2xl bg-gradient-to-r from-slate-900 to-slate-700 p-8 text-white shadow-lg">
        <h1 className="text-3xl font-bold">
          Bienvenido al Centro de Datos y BI
        </h1>

        <p className="mt-2 text-slate-300">
          Desde aquí puedes administrar usuarios, consultar reportes y visualizar
          la información más importante del sistema.
        </p>
      </div>

			<div className="flex justify-center my-2">
  <img
    src="/probando2.png"
    alt="Dashboard"
    className="w-128 rounded-xl"
  />
</div>


      <div className="mt-8">
        <div className="rounded-xl bg-white p-6 shadow">
          <i className="fa fa-users text-3xl text-blue-500"></i>

          <p className="text-sm text-slate-500">
            Este es un centro integral para la gestión de informes y análisis de Business Intelligence (BI). Nuestra plataforma está diseñada para centralizar y facilitar el acceso a una variedad de reportes y datos clave, proporcionando una visión clara y detallada de la información crítica para la organización.
          </p>
        </div>
      </div>
    </div>
  );
}