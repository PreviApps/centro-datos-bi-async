import { ChartColumnStacked } from "@gravity-ui/icons";
import CustomMainContent from "./common/custom_main_content/CustomMainContent";
import CustomNavbar from "./common/custom_navbar/CustomNavbar";
import { Button, Modal, Tooltip } from "@heroui/react";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { ToastService } from "../utils/ToastService";
import { deleteBoard, getBoard, getBoards, getBoardsByUser } from "../api/boards";
import { CustomGridCard } from "./common/custom_grid_card/CustomGridCard";
import { CustomModalBlur } from "./common/custom_modal_blur/CustomModalBlur";
import { useAuth } from "../context/AuthContext";


export default function BoardsPage() {

	const navigate = useNavigate();
	const { user } = useAuth();

	const [boards, setBoards] = useState<any[]>([]);
	const [selectedBoard, setSelectedBoard] = useState<any>(null);
	const [isModalOpen, setIsModalOpen] = useState(false);

	const [fetchingBoards, setFetchingBoards] = useState(true);
	const [loading, setLoading] = useState(false);

	useEffect(() => {
		if (user?.id) {
			loadBoards(user.id);
		}
	}, [user]);

	async function loadBoards(userId: string) {
		setFetchingBoards(true);
		try {
			const data = await ToastService.execute({
				action: () => getBoardsByUser(userId, user?.collaborator_position_name), 
				loading: "Cargando tus tableros...",
				success: () => "Tableros cargados",
				error: "No fue posible cargar los tableros"
			});
			setBoards(data || []);
		} catch (error) {
			console.error("ERROR LOADING BOARDS:", error);
			setBoards([]);
		} finally {
			setFetchingBoards(false);
		}
	}

	async function handleSelectBoard(boardId: string) {
		try {
			const board = await ToastService.execute({
				action: () => getBoard(boardId),
				loading: "Cargando tablero...",
				success: "Tablero cargado",
				error: "No fue posible obtener el tablero."
			});
			setSelectedBoard(board);
			setIsModalOpen(true);
		} catch (error) {
			console.error(error);
		}
	}

	const handleEditBoard = () => {
		if (!selectedBoard) return;
		setIsModalOpen(false); // Cerramos el modal primero
		navigate("/create-board", { state: { boardId: selectedBoard.id } });
	};

	const handleDeleteBoard = async () => {
		if (!selectedBoard) return;

		if (!confirm(`¿Eliminar "${selectedBoard.name}"?`)) {
			return;
		}

		try {
			await ToastService.execute({
				action: () => deleteBoard(selectedBoard.id),
				loading: "Eliminando tablero...",
				success: "Tablero eliminado.",
				error: "No fue posible eliminar el tablero"
			});

			setIsModalOpen(false);
			if (user?.id) loadBoards(user.id);
		} catch (err) {
			console.error(err);
		}
	};

	// Acción para ver/abrir el reporte embebido de Power BI
	const handleViewPowerBI = () => {
		if (!selectedBoard) return;
		setIsModalOpen(false);
		// Redirige a la vista del visor que construimos antes, pasando el id o la url
		navigate(`/boards/view/${selectedBoard.id}`);
	};

	return (
		<>
			<CustomNavbar title="Módulo de tableros">
				<p>Consulta y busca los tableros disponibles</p>
			</CustomNavbar>
			<CustomMainContent>
				<Tooltip delay={0}>
					<Button onClick={() => navigate("/create-board")} isIconOnly variant="ghost"
						className="fixed bottom-6 right-6 z-50 h-12 w-12 rounded-full shadow-lg">
						<ChartColumnStacked className="h-8 w-8" />
					</Button>
					<Tooltip.Content>
						<p>Nuevo tablero</p>
					</Tooltip.Content>
				</Tooltip>
				<CustomModalBlur
					isOpen={isModalOpen}
					onOpenChange={setIsModalOpen}
				>
					{selectedBoard && (
						<Modal.Dialog className="sm:max-w-[500px]">
							<Modal.Header>
								<Modal.Heading>
									{selectedBoard.name}
								</Modal.Heading>
							</Modal.Header>

							<Modal.Body>
								<p className="text-default-600 mb-2">{selectedBoard.description || "Sin descripción"}</p>

								{/*<div className="text-xs text-default-400 space-y-1 border-t border-default-100 pt-3">
									<p><strong className="text-default-600">Workspace ID:</strong> {selectedBoard.workspace_id}</p>
									<p><strong className="text-default-600">Report ID:</strong> {selectedBoard.powerbi_report_id}</p>
								</div>*/}
							</Modal.Body>

							<Modal.Footer className="flex items-center justify-between gap-2">
								<div className="flex gap-2">
									<Button
										variant="ghost"
										onPress={handleDeleteBoard}
										isDisabled={loading}
									>
										Eliminar
									</Button>
									<Button
										variant="outline"
										onPress={handleEditBoard}
										isDisabled={loading}
									>
										Editar
									</Button>
								</div>

								<Button
									onPress={handleViewPowerBI}
									isPending={loading}
								>
									Ver Tablero
								</Button>
							</Modal.Footer>
						</Modal.Dialog>
					)}
				</CustomModalBlur>
				{fetchingBoards ? (
					<p>Cargando tableros...</p>
				) : boards.length === 0 ? (
					<div className="flex flex-col items-center justify-center py-16 text-center">
						<h3 className="text-lg font-semibold">
							No se encontraron tableros
						</h3>
						<p className="mt-2 text-default-500">
							No hay tableros de Power BI disponibles para mostrar.
						</p>
					</div>
				) : (
					<CustomGridCard
						items={boards}
						onItemClick={(board) => handleSelectBoard(board.id)}
						renderItem={(board) => ({
							id: board.id,
							title: board.name,
							description: board.description
						})}
					/>
				)}
			</CustomMainContent>
		</>
	)
}