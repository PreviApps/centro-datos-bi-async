import { useEffect, useState } from "react";

import {
  getReports,
  getReport,
  runReport,
  deleteReport
} from "../api/reports"

import { getJob } from "../api/jobs";

import { pollJob } from "../utils/polljob";
import { CustomGridCard } from "./common/custom_grid_card/CustomGridCard";
import { CustomModalBlur } from "./common/custom_modal_blur/CustomModalBlur";
import { Button, Modal, Input, Checkbox, Tooltip } from "@heroui/react";
import { ToastService } from "../utils/ToastService";
import CustomNavbar from "./common/custom_navbar/CustomNavbar";
import CustomMainContent from "./common/custom_main_content/CustomMainContent";
import { useNavigate } from "react-router-dom";
import { ChartMixed } from "@gravity-ui/icons";

export default function ReportsPage() {

  const navigate = useNavigate();

  const [reports, setReports] = useState<any[]>([]);
  const [selectedReport, setSelectedReport] = useState<any>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [fetchingReports, setFetchingReports] = useState(true);
  const [loading, setLoading] = useState(false);
  const [paramValues, setParamValues] = useState<Record<string, any>>({});

  useEffect(() => {
    loadReports();
  }, []);

  async function loadReports() {
    setFetchingReports(true);
    try {
      const data = await ToastService.execute({
        action: getReports,
        loading: "Cargando reportes...",
        success: () => "Reportes cargados",
        error: "No fue posible cargar los reportes"
      });
      //console.log("REPORTS:", data);
      setReports(data || []);
    } catch (error) {
      console.error("ERROR LOADING REPORTS:", error);
      setReports([])
    } finally {
      setFetchingReports(false);
    }
  }

  async function handleSelectReport(reportId: string) {

    try {

      const report = await ToastService.execute({
        action: () => getReport(reportId),
        loading: "Cargando reporte...",
        success: "Reporte cargado",
        error: "No fue posible obtener el reporte."
      });
      setSelectedReport(report);

      const initialParams: Record<string, any> = {};

      if (report?.parameters && Array.isArray(report.parameters)) {
        report.parameters.forEach((param: any) => {
          initialParams[param.name] = param.default ?? (param.type === "boolean" ? false : "");
        });
      }
      setParamValues(initialParams);

      setIsModalOpen(true);

    } catch (error) {
      console.error(error);
    }
  }

  /*const handleParamChange = (name: string, value: any) => {
    setParamValues((prev) => ({
      ...prev,
      [name]: paramValues
    }));
  };*/

  const handleParamChange = (name: string, value: any) => {
    setParamValues((prev) => ({
      ...prev,
      [name]: value
    }));
  };

  const handleEditReport = () => {
    if (!selectedReport) return;
    setIsModalOpen(false); // Cerramos el modal primero
    navigate("/create-report", { state: { reportId: selectedReport.id } });
  };

  const handleDeleteReport = async () => {

    if (!selectedReport) return;

    if (!confirm(`¿Eliminar "${selectedReport.name}"?`)) {
      return;
    }

    try {

      await ToastService.execute({

        action: () => deleteReport(selectedReport.id),

        loading: "Eliminando reporte...",

        success: "Reporte eliminado.",

        error: "No fue posible eliminar el reporte"

      });

      setIsModalOpen(false);

      loadReports();

    } catch (err) {

      console.error(err);

    }

  };

  async function handleRunReport() {

    if (!selectedReport) return;

    setLoading(true);

    try {

      await ToastService.execute({
        action: async () => {
          const response = await runReport(selectedReport.id, paramValues);
          const jobId = response.job_id;

          const finalJob = await pollJob(
            () => getJob(jobId),
            (job) => job.status === "success" || job.status === "failed",
            { interval: 3000 }
          );

          if (finalJob.status === "failed") {
            throw new Error(finalJob.error || "Falló la generación del reporte");
          }

          if (finalJob.status === "success" && finalJob.download_url) {
            const link = document.createElement("a");
            link.href = finalJob.download_url;
            link.download = "";
            document.body.appendChild(link);
            link.click();
            link.remove();
          }

          return finalJob;
        },
        loading: "Generando reporte...",
        success: "Reporte generado correctamente",
        error: (err: any) => err?.message || "Error al procesar el reporte"
      });

      setIsModalOpen(false);

    } catch (error) {

      console.error(error);

    } finally {

      setLoading(false);
    }
  }

  // 🎨 Versión corregida con Inputs nativos estilizados (100% segura en TypeScript)
  const renderParamInput = (param: { name: string; type: string; required: boolean }) => {
    const labelName = param.name.replace(/_/g, " ").toUpperCase();

    // Clases de Tailwind comunes para mantener la estética limpia y moderna
    const inputClasses = "w-full px-3 py-2 border rounded-lg bg-default-50 border-default-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50";

    switch (param.type) {
      case "date":
        return (
          <div key={param.name} className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-default-600">{labelName}</label>
            <input
              type="date"
              className={inputClasses}
              required={param.required}
              value={paramValues[param.name] || ""}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                handleParamChange(param.name, e.target.value)
              }
            />
          </div>
        );
      case "number":
        return (
          <div key={param.name} className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-default-600">{labelName}</label>
            <input
              type="number"
              placeholder="0"
              className={inputClasses}
              required={param.required}
              value={paramValues[param.name] || ""}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                handleParamChange(param.name, e.target.value)
              }
            />
          </div>
        );
      case "boolean":
        return (
          <div key={param.name} className="flex items-center py-1 gap-2.5 select-none">
            <input
              type="checkbox"
              id={`chk-${param.name}`}
              className="h-4 w-4 rounded border-default-300 text-primary-600 focus:ring-primary-500"
              checked={!!paramValues[param.name]}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                handleParamChange(param.name, e.target.checked)
              }
            />
            <label htmlFor={`chk-${param.name}`} className="text-xs font-semibold text-default-600 cursor-pointer">
              {labelName}
            </label>
          </div>
        );
      case "string":
      default:
        return (
          <div key={param.name} className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-default-600">{labelName}</label>
            <input
              type="text"
              placeholder={`Escribe ${labelName.toLowerCase()}...`}
              className={inputClasses}
              required={param.required}
              value={paramValues[param.name] || ""}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                handleParamChange(param.name, e.target.value)
              }
            />
          </div>
        );
    }
  };

  return (
    <div>
      <CustomNavbar title="Módulo de reportes">
        <p>Consulta y busca los reportes disponibles</p>
      </CustomNavbar>
      <CustomMainContent>
        <Tooltip delay={0}>
          <Button onClick={() => navigate("/create-report")} isIconOnly variant="ghost"
            className="fixed bottom-6 right-6 z-50 h-12 w-12 rounded-full shadow-lg">
            <ChartMixed className="h-8 w-8" />
          </Button>
          <Tooltip.Content>
            <p>Nuevo reporte</p>
          </Tooltip.Content>
        </Tooltip>

        <CustomModalBlur
          isOpen={isModalOpen}
          onOpenChange={setIsModalOpen}
        >
          {selectedReport && (
            <Modal.Dialog className="sm:max-w-[500px]">
              <Modal.Header>
                <Modal.Heading>
                  {selectedReport.name}
                </Modal.Heading>
              </Modal.Header>

              <Modal.Body>
                <p>{selectedReport.description}</p>

                {/* Aquí luego puedes agregar los parámetros dinámicos */}
                {selectedReport.parameters && selectedReport.parameters.length > 0 ? (
                  <div className="space-y-4 border-t border-default-100 pt-4">
                    <h4 className="text-sm font-semibold text-default-700">Parámetros del reporte:</h4>
                    {selectedReport.parameters.map((param: any) => renderParamInput(param))}
                  </div>
                ) : (
                  <p className="text-xs text-default-400 italic border-t border-default-100 pt-2">
                    Este reporte no requiere parámetros.
                  </p>
                )}
              </Modal.Body>

              {/*<Modal.Footer>
                <Button
                  variant="outline"
                  onPress={handleRunReport}
                  isPending={loading}
                >
                  Run report
                </Button>
              </Modal.Footer>*/}

              <Modal.Footer className="flex items-center justify-between gap-2">
                {/* Botones secundarios / de acción directa al reporte */}
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    onPress={handleDeleteReport}
                    isDisabled={loading}
                  >
                    Eliminar
                  </Button>
                  <Button
                    variant="outline"
                    onPress={handleEditReport}
                    isDisabled={loading}
                  >
                    Editar
                  </Button>
                </div>

                {/* Botón principal */}
                <Button
                  onPress={handleRunReport}
                  isPending={loading}
                >
                  Run report
                </Button>
              </Modal.Footer>
            </Modal.Dialog>
          )}
        </CustomModalBlur>

        {fetchingReports ? (
          <p>Cargando reportes...</p>
        ) : reports.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <h3 className="text-lg font-semibold">
              No se encontraron reportes
            </h3>
            <p className="mt-2 text-default-500">
              No hay reportes disponibles para mostrar.
            </p>
          </div>
        ) : (
          <CustomGridCard
            items={reports}
            onItemClick={(report) => handleSelectReport(report.id)}
            renderItem={(report) => ({
              id: report.id,
              title: report.name,
              description: report.description
            })}
          />
        )}
      </CustomMainContent>
    </div>
  );
}