import { useEffect, useState } from 'react'
import { ChevronLeft, FolderTree, SquareListUl } from '@gravity-ui/icons';
import { Button, Card, Typography } from '@heroui/react'
import SqlEditor from '../sql_editor';
import { useMinioExplorer } from '../../hooks/use_minio_explorer';
import { previewParquet } from '../../api/preview_parquet';
import PreviewTable from '../preview_table';
import { CustomGridCard } from '../common/custom_grid_card/CustomGridCard';
import { MinioItem } from '../../utils/interfaces/minio/minio.interface';
import { pollJob } from '../../utils/polljob';
import { getJob } from '../../api/jobs';
import DataTableCard from '../../utils/DataTableCard';
import { useLocation } from 'react-router-dom';
import { getReport } from '../../api/reports';

export default function ReportsContent() {

	const location = useLocation();
	const editingReportId = location.state?.reportId || null;

	const [reportToEdit, setReportToEdit] = useState<any>(null);
	const [isLoadingReport, setIsLoadingReport] = useState<boolean>(false);

	const {
		path,
		items,
		openFolder,
		goBack
	} = useMinioExplorer()

	const [parquetPreview, setParquetPreview] =
		useState(null);

	const [sqlPreview, setSqlPreview] = useState(null);

	const [isParquetLoading, setIsParquetLoading] = useState(false);
	const [isQueryLoading, setIsQueryLoading] = useState(false);

	useEffect(() => {
		if (editingReportId) {
			loadReportToEdit(editingReportId);
		}
	}, [editingReportId]);

	async function loadReportToEdit(id: string) {
		try {
			setIsLoadingReport(true);
			const reportData = await getReport(id);
			console.log("REPORTE A EDITAR", reportData);
			setReportToEdit(reportData);
		} catch (error) {
			console.error("Error cargando el reporte para editar", error);
		}finally{
			setIsLoadingReport(false);
		}
	}

	const handleClick = async (item: MinioItem) => {

		const isFolder = item.object_name.endsWith("/")

		const isParquet = item.object_name.endsWith(".parquet");

		if (isFolder) {
			openFolder(item.object_name)
			return;
		}

		if (isParquet) {

			try {
				setIsParquetLoading(true);
				setParquetPreview(null);

				const response = await previewParquet(item.object_name);

				console.log("JOB BIEN PREVIEW", response)

				const jobId = response.job_id;

				if (!jobId) {
					throw new Error("No se recibió job desde el backend")
				}

				const finalJob = await pollJob(
					() => getJob(jobId),
					(job) => job.status === "success" || job.status === "failed", // Condición de parada
					{
						interval: 1500, // Revisa cada 1.5 segundos
						timeout: 1000 * 60 * 3 // Cancela tras 3 minutos máximo
					}
				);

				if (finalJob.status === "success") {
					// Extraemos los datos desde la nueva columna JSONB que creamos en Postgres
					setParquetPreview(finalJob.preview_results);
				} else {
					alert(finalJob.error || "Error al generar la vista previa del Parquet");
				}
			} catch (err) {

				console.error(err);
			} finally {
				setIsParquetLoading(false);
			}
		}
	}
	console.log("ITEMS RENDER:", items);

	return (
		<>
		{/* Pequeño aviso visual solo si estamos editando */}
            {editingReportId && (
                <div className="mb-4 p-3 bg-amber-500/10 border border-amber-500/20 text-amber-600 rounded-lg text-sm flex items-center justify-between">
                    <span>
                        Modo edición: <strong>{reportToEdit?.name || "Cargando..."}</strong>
                    </span>
                </div>
            )}
			<div className="grid gap-6 lg:grid-cols-2">

				<Card.Root className="max-h-[500px] flex flex-col">
					<Card.Header>
						<Card.Title>Explorador MinIO</Card.Title>
					</Card.Header>

					<Card.Content className="overflow-y-auto flex-1 pr-2">
						<Button
							onClick={goBack}
							isIconOnly
							variant="outline"
						>
							<ChevronLeft />
						</Button>

						{items.map((item, i) => (
							<p
								key={i}
								style={{ cursor: "pointer", display: "flex", alignItems: "center", gap: "8px" }}
								onClick={() => handleClick(item)}
							>
								{item.object_name.includes(".parquet") ? (
									<SquareListUl />
								) : (
									<FolderTree />
								)}
								{item.object_name}
							</p>
						))}
					</Card.Content>
				</Card.Root>

				<Card.Root>
					<Card.Header>
						<Card.Title>{editingReportId ? 'Editar Consulta SQL' : 'SQL Editor'}</Card.Title>
					</Card.Header>

					<Card.Content>
						<SqlEditor initialValue={reportToEdit?.sql_template || reportToEdit?.query || ''} setSqlPreview={setSqlPreview} setIsQueryLoading={setIsQueryLoading} reportToEdit={reportToEdit}/>
					</Card.Content>
				</Card.Root>

				{/*<DataTableCard title="Parquet Preview">
					<PreviewTable
						data={parquetPreview}
						loading={isParquetLoading}
						message="Selecciona un parquet"
					/>
				</DataTableCard>

				<DataTableCard title="Query Result">
					<PreviewTable
						data={sqlPreview}
						loading={isQueryLoading}
						message="Ejecuta una query"
					/>
				</DataTableCard>*/}

				{/* PARQUET PREVIEW CON SCROLL */}
				<DataTableCard title="Parquet Preview">
					<div className="max-h-[400px] overflow-auto">
						<PreviewTable
							data={parquetPreview}
							loading={isParquetLoading}
							message="Selecciona un parquet"
						/>
					</div>
				</DataTableCard>

				{/* QUERY RESULT CON SCROLL */}
				<DataTableCard title="Query Result">
					<div className="max-h-[400px] overflow-auto">
						<PreviewTable
							data={sqlPreview}
							loading={isQueryLoading}
							message="Ejecuta una query"
						/>
					</div>
				</DataTableCard>
			</div>
		</>
	)
}