import { useEffect, useState } from "react";
import CustomMainContent from "../common/custom_main_content/CustomMainContent";
import CustomNavbar from "../common/custom_navbar/CustomNavbar";
import { CustomGridCard } from "../common/custom_grid_card/CustomGridCard";
import { CustomModalBlur } from "../common/custom_modal_blur/CustomModalBlur";
import { CustomTabs, TabItem } from "../common/custom_tabs/CustomTabs";
import { Button, Checkbox, SearchField } from "@heroui/react";
import { ToastService } from "../../utils/ToastService";
import { getReports } from "../../api/reports";
import { getBoards } from "../../api/boards";
import {
	getReportUsersWithPermissions,
	updateReportPermissions,
	getBoardUsersWithPermissions,
	updateBoardPermissions
} from "../../api/permissions";

export default function AdminContent() {
	const [reports, setReports] = useState<any[]>([]);
	const [boards, setBoards] = useState<any[]>([]);
	const [fetchingItems, setFetchingItems] = useState(true);
	const [activeTab, setActiveTab] = useState<"reports" | "boards">("reports");

	const [isModalOpen, setIsModalOpen] = useState(false);
	const [loading, setLoading] = useState(false);
	const [selectedItem, setSelectedItem] = useState<any>(null);
	const [searchQuery, setSearchQuery] = useState("");

	const [allUsers, setAllUsers] = useState<any[]>([]);
	const [grantedUsers, setGrantedUsers] = useState<string[]>([]);

	useEffect(() => {
		loadData();
	}, []);

	async function loadData() {
		setFetchingItems(true);
		try {
			const reportsData = await getReports();
			const boardsData = await getBoards();
			setReports(reportsData || []);
			setBoards(boardsData || []);
		} catch (error) {
			console.error("ERROR LOADING ADMIN DATA:", error);
		} finally {
			setFetchingItems(false);
		}
	}

	const handleCardClick = async (item: any, type: "reports" | "boards") => {
		setActiveTab(type);
		setSelectedItem(item);
		setSearchQuery("");

		try {
			const fetchFn = type === "reports" ? getReportUsersWithPermissions : getBoardUsersWithPermissions;
			const usersList = await ToastService.execute({
				action: () => fetchFn(item.id),
				loading: "Cargando usuarios y permisos...",
				success: "Datos cargados",
				error: "No fue posible obtener los accesos"
			});

			setAllUsers(usersList || []);

			const initialGranted = (usersList || [])
				.filter((u: any) => u.has_permission)
				.map((u: any) => u.id);

			setGrantedUsers(initialGranted);
			setIsModalOpen(true);
		} catch (error) {
			console.error("Error al abrir modal de permisos:", error);
		}
	};

	const toggleUserGrant = (userId: string) => {
		setGrantedUsers((prev) =>
			prev.includes(userId) ? prev.filter((id) => id !== userId) : [...prev, userId]
		);
	};

	const handleSavePermissions = async () => {
		if (!selectedItem) return;

		setLoading(true);
		try {
			const updateFn = activeTab === "reports" ? updateReportPermissions : updateBoardPermissions;

			await ToastService.execute({
				action: () =>
					updateFn(selectedItem.id, {
						user_ids: grantedUsers,
						position_names: [],
						admin_user_id: "admin-sso-id"
					}),
				loading: "Guardando asignaciones...",
				success: "Permisos actualizados correctamente",
				error: "No fue posible guardar los cambios"
			});

			setIsModalOpen(false);
		} catch (error) {
			console.error("Error al guardar permisos:", error);
		} finally {
			setLoading(false);
		}
	};

	const filteredUsers = allUsers.filter((user) => {
		const query = searchQuery.toLowerCase();
		const matchName = user.name?.toLowerCase().includes(query) || false;
		const matchPosition = user.collaborator_position_name?.toLowerCase().includes(query) || false;
		return matchName || matchPosition;
	});

	const mainSectionTabs: TabItem[] = [
		{
			id: "reports",
			label: "Reportes",
			showSeparator: false,
			content: fetchingItems ? (
				<p className="text-center py-8">Cargando reportes...</p>
			) : (
				<CustomGridCard
					items={reports}
					renderItem={(item) => ({
						id: item.id,
						title: item.name,
						description: item.description,
					})}
					onItemClick={(item) => handleCardClick(item, "reports")}
				/>
			),
		},
		{
			id: "boards",
			label: "Tableros",
			showSeparator: true,
			content: fetchingItems ? (
				<p className="text-center py-8">Cargando tableros...</p>
			) : (
				<CustomGridCard
					items={boards}
					renderItem={(item) => ({
						id: item.id,
						title: item.name,
						description: item.description,
					})}
					onItemClick={(item) => handleCardClick(item, "boards")}
				/>
			),
		},
	];

	return (
		<>
			<CustomNavbar title="Módulo de administración">
				<p>Consulta y administra los permisos de acceso para reportes y tableros</p>
			</CustomNavbar>

			<CustomMainContent>
				<div className="flex flex-col items-center w-full max-w-6xl mx-auto p-4 gap-6">
					<h1 className="text-2xl font-bold text-center">Gestión de Accesos</h1>

					<div className="w-full">
						<CustomTabs items={mainSectionTabs} />
					</div>
				</div>

				<CustomModalBlur
					isOpen={isModalOpen}
					onOpenChange={(open) => {
						setIsModalOpen(open);
						if (!open) {
							setSearchQuery("");
							setSelectedItem(null);
						}
					}}
				>
					<div
						onClick={(e) => e.stopPropagation()}
						className="w-[750px] max-w-full max-h-[85vh] h-fit p-6 bg-white dark:bg-zinc-900 rounded-xl flex flex-col gap-4 shadow-xl overflow-hidden"
					>
						<div className="flex-shrink-0">
							<h2 className="text-xl font-bold">Asignar Permisos</h2>
							{selectedItem && (
								<p className="text-sm text-zinc-500">
									Configurando accesos para ({activeTab === "reports" ? "Reporte" : "Tablero"}): <span className="font-semibold text-primary">{selectedItem.name}</span>
								</p>
							)}
						</div>

						<div className="w-full pt-2 flex-shrink-0">
							<SearchField name="user-search" value={searchQuery} onChange={setSearchQuery}>
								<SearchField.Group className="w-full">
									<SearchField.SearchIcon />
									<SearchField.Input placeholder="Buscar por nombre de usuario o cargo..." />
									<SearchField.ClearButton />
								</SearchField.Group>
							</SearchField>
						</div>

						{filteredUsers.length > 0 && (
							<div className="flex items-center px-3 py-2 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg border border-zinc-200 dark:border-zinc-800 flex-shrink-0">
								{(() => {
									const filteredIds = filteredUsers.map((u) => u.id);
									const allFilteredAreChecked = filteredIds.every((id) => grantedUsers.includes(id));

									const handleSelectAllToggle = () => {
										if (allFilteredAreChecked) {
											setGrantedUsers((prev) => prev.filter((id) => !filteredIds.includes(id)));
										} else {
											setGrantedUsers((prev) => Array.from(new Set([...prev, ...filteredIds])));
										}
									};

									return (
										<div
											onClick={handleSelectAllToggle}
											className="flex items-center justify-between w-full cursor-pointer select-none"
										>
											<span className="text-xs font-semibold text-zinc-600 dark:text-zinc-400">
												{allFilteredAreChecked ? "Deseleccionar todos los filtrados" : "Seleccionar todos los filtrados"} ({filteredUsers.length})
											</span>
											<Checkbox
												isSelected={allFilteredAreChecked}
												onChange={handleSelectAllToggle}
											>
												<Checkbox.Content>
													<Checkbox.Control>
														<Checkbox.Indicator />
													</Checkbox.Control>
												</Checkbox.Content>
											</Checkbox>
										</div>
									);
								})()}
							</div>
						)}

						<div className="flex flex-col gap-2 overflow-y-auto pr-1 flex-1 min-h-[150px] max-h-[50vh]">
							{filteredUsers.length > 0 ? (
								filteredUsers.map((user) => {
									const isChecked = grantedUsers.includes(user.id);
									return (
										<div
											key={user.id}
											onClick={() => toggleUserGrant(user.id)}
											className={`flex items-center justify-between p-3 border rounded-lg cursor-pointer transition-colors ${isChecked ? "border-primary bg-primary/5" : "border-zinc-200 dark:border-zinc-800"}`}
										>
											<div className="flex flex-col pointer-events-none">
												<span className="font-semibold text-sm">{user.name}</span>
												<span className="text-xs text-zinc-500">
													Cargo: <span className="font-medium text-zinc-700 dark:text-zinc-300">{user.collaborator_position_name}</span> ({user.corporate_email})
												</span>
											</div>

											<Checkbox
												isSelected={isChecked}
												onChange={() => toggleUserGrant(user.id)}
											>
												<Checkbox.Content>
													<Checkbox.Control>
														<Checkbox.Indicator />
													</Checkbox.Control>
												</Checkbox.Content>
											</Checkbox>
										</div>
									);
								})
							) : (
								<p className="text-center text-sm text-zinc-400 py-6">No se encontraron usuarios o cargos coincidentes.</p>
							)}
						</div>

						<div className="flex justify-end gap-2 pt-4 border-t flex-shrink-0">
							<Button onPress={() => setIsModalOpen(false)} isDisabled={loading}>
								Cancelar
							</Button>
							<Button variant="primary" onPress={handleSavePermissions} isPending={loading}>
								Guardar Asignaciones
							</Button>
						</div>
					</div>
				</CustomModalBlur>
			</CustomMainContent>
		</>
	);
}