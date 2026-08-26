import { createBoard, getBoard, getPowerBIReports, getPowerBIWorkspaces, updateBoard } from "../../api/boards";
import { Card, Input, Label, ListBox, Select, TextArea, TextField } from "@heroui/react";
import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { CustomForm } from "../common/custom_form/CustomForm";
import { useAuth } from "../../context/AuthContext";
import { ToastService } from "../../utils/ToastService";

export default function BoardsContent() {

	const location = useLocation();
	const navigate = useNavigate();
	const { user } = useAuth();
	const editingBoardId = location.state?.boardId || null;

	const [boardToEdit, setBoardToEdit] = useState<any>(null);
	const [isLoadingBoard, setIsLoadingBoard] = useState<boolean>(false);
	const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

	// Listas dinámicas para Power BI
	const [workspaces, setWorkspaces] = useState<any[]>([]);
	const [reports, setReports] = useState<any[]>([]);
	const [isLoadingReports, setIsLoadingReports] = useState<boolean>(false);

	// Estado del formulario
	const [formValues, setFormValues] = useState({
		name: "",
		description: "",
		workspace_id: "",
		powerbi_report_id: "",
		embed_url: "",
	});

	useEffect(() => {
		loadWorkspaces();
		if (editingBoardId) {
			loadBoardToEdit(editingBoardId);
		}
	}, [editingBoardId]);

	async function loadWorkspaces() {
		try {
			const data = await getPowerBIWorkspaces();
			setWorkspaces(data || []);
		} catch (error) {
			console.error("Error al cargar workspaces", error);
		}
	}

	async function loadBoardToEdit(id: string) {
		try {
			setIsLoadingBoard(true);
			const boardData = await ToastService.execute({
				action: () => getBoard(id),
				loading: "Cargando tablero...",
				success: "Tablero cargado",
				error: "No fue posible cargar el tablero"
			});

			setBoardToEdit(boardData);
			setFormValues({
				name: boardData.name || "",
				description: boardData.description || "",
				workspace_id: boardData.workspace_id || "",
				powerbi_report_id: boardData.powerbi_report_id || "",
				embed_url: boardData.embed_url || "",
			});

			// Si tiene workspace asignado, cargamos sus reportes para que el select los muestre
			if (boardData.workspace_id) {
				const reportsData = await getPowerBIReports(boardData.workspace_id);
				setReports(reportsData || []);
			}
		} catch (error) {
			console.error("Error cargando el tablero para editar", error);
		} finally {
			setIsLoadingBoard(false);
		}
	}

	const handleWorkspaceChange = async (workspaceId: string) => {
		setFormValues((prev) => ({
			...prev,
			workspace_id: workspaceId,
			powerbi_report_id: "",
			embed_url: "",
		}));
		setReports([]);

		if (!workspaceId) return;

		try {
			setIsLoadingReports(true);
			const data = await getPowerBIReports(workspaceId);
			setReports(data || []);
		} catch (error) {
			console.error("Error al cargar reportes", error);
		} finally {
			setIsLoadingReports(false);
		}
	};

	const handleReportChange = (reportId: string) => {
		const selectedReport = reports.find((r) => r.id === reportId);
		if (selectedReport) {
			setFormValues((prev) => ({
				...prev,
				powerbi_report_id: selectedReport.id,
				embed_url: selectedReport.embedUrl,
				name: prev.name || selectedReport.name,
			}));
		}
	};

	const handleChange = (field: string, value: string) => {
		setFormValues((prev) => ({ ...prev, [field]: value }));
	};

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!user?.id) return;

		try {
			setIsSubmitting(true);
			await ToastService.execute({
				action: async () => {
					if (editingBoardId) {
						return await updateBoard(editingBoardId, {
							...formValues,
							updated_by: user.id,
						});
					} else {
						return await createBoard({
							...formValues,
							created_by: user.id,
						});
					}
				},
				loading: editingBoardId ? "Actualizando tablero..." : "Creando tablero...",
				success: editingBoardId ? "Tablero actualizado correctamente" : "Tablero creado correctamente",
				error: "No fue posible guardar el tablero"
			});

			navigate("/boards");
		} catch (error) {
			console.error("Error al guardar el tablero", error);
		} finally {
			setIsSubmitting(false);
		}
	};

	return (
		<>
			<div className="w-full max-w-6xl mx-auto p-4 sm:p-6">
				{/* Pequeño aviso visual solo si estamos editando */}
				{editingBoardId && (
					<div className="mb-4 p-3 bg-amber-500/10 border border-amber-500/20 text-amber-600 rounded-lg text-sm flex items-center justify-between">
						<span>
							Modo edición: <strong>{boardToEdit?.name || "Cargando..."}</strong>
						</span>
					</div>
				)}
				<Card.Root className="w-full max-w-5xl mx-auto">
					<Card.Header>
						<Card.Title>{editingBoardId ? 'Editar Tablero' : 'Board Create'}</Card.Title>
					</Card.Header>

					<Card.Content>
						<div className="w-full max-w-3xl">
							<CustomForm onSubmit={handleSubmit}>
								<TextField value={formValues.name} onChange={(val) => handleChange('name', val)}>
									<Label>Nombre del tablero</Label>
									<Input placeholder="Nombre del tablero"></Input>
								</TextField>
								<div>
									<Label>Descripción</Label>
									<TextArea
										variant="primary"
										className="w-full min-h-32"
										value={formValues.description}
										onChange={(e) => handleChange("description", e.target.value)}
										placeholder="This board facturation data"
									/>
								</div>
								<div>
									<Select
										variant="primary"
										selectedKey={formValues.workspace_id}
										onChange={(key) => handleWorkspaceChange(String(key))}>
										<Label>Área de trabajo</Label>
										<Select.Trigger>
											<Select.Value>
												{workspaces.find(w => w.id === formValues.workspace_id)?.name || "Selecciona un workspace"}
											</Select.Value>
											<Select.Indicator />
										</Select.Trigger>
										<Select.Popover>
											<ListBox>
												{workspaces.map((ws) => (
													<ListBox.Item key={ws.id} id={ws.id} textValue={ws.name}>
														{ws.name}
													</ListBox.Item>
												))}
											</ListBox>
										</Select.Popover>
									</Select>
								</div>
								<div>
									<Select
										variant="primary"
										selectedKey={formValues.powerbi_report_id}
										onSelectionChange={(key) => handleReportChange(String(key))}
										isDisabled={!formValues.workspace_id || isLoadingReports}
									>
										<Label>Tablero</Label>
										<Select.Trigger>
											<Select.Value>
												{isLoadingReports
													? "Cargando..."
													: reports.find(r => r.id === formValues.powerbi_report_id)?.name || "Selecciona un tablero"}
											</Select.Value>
											<Select.Indicator />
										</Select.Trigger>
										<Select.Popover>
											<ListBox>
												{reports.map((report) => (
													<ListBox.Item key={report.id} id={report.id} textValue={report.name}>
														{report.name}
													</ListBox.Item>
												))}
											</ListBox>
										</Select.Popover>
									</Select>
								</div>
							</CustomForm>
						</div>
					</Card.Content>
				</Card.Root>
			</div>
		</>
	)
}