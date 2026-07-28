import { useEffect, useState } from "react";
import { listTables } from "../api/tables";
import { MinioItem } from "../utils/interfaces/minio/minio.interface";

export function useMinioExplorer(initialPath = "") {

	const [path, setPath] = useState(initialPath);
	const [items, setItems] = useState<MinioItem[]>([]);

	useEffect(() => {
		listTables(path)
			.then((data) => {
				const filteredItems = (data.items ?? []).filter(
					(item) =>
						item.object_name !== "openmetadata.json" &&
						item.object_name !== "temp/"
				);

				setItems(filteredItems);
			})
			.catch(console.error);
	}, [path]);

	const openFolder = (folderPath: string) => {
		setPath(folderPath);
	};

	const goBack = () => {

		if (!path) return;

		// quitar slash final
		const trimmed = path.endsWith("/")
			? path.slice(0, -1)
			: path;

		// dividir segmentos
		const parts = trimmed.split("/");

		// quitar último folder
		parts.pop();

		// reconstruir path
		const previousPath =
			parts.length > 0
				? parts.join("/") + "/"
				: "";

		setPath(previousPath);
	};

	return {
		path,
		items,
		openFolder,
		goBack
	};
}