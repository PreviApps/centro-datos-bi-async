import { Card } from "@heroui/react";

interface CustomGridCardProps<T> {
	items: T[]
	renderItem: (item: T) => {
		id: string
		title: string
		description: string
	}
	onItemClick?: (item: T) => void
}

export function CustomGridCard<T>({ items, renderItem, onItemClick }: CustomGridCardProps<T>) {
	return (
		<div className="grid gap-4" style={{
			gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))",
		}}>
			{items.map((item, index) => {
				const { id, title, description } = renderItem(item)
				return (
					<Card variant="transparent" key={id || index} className="shadow-sm border" style={{ cursor: "pointer" }}
						onClick={() => onItemClick?.(item)}>
						<Card.Header>
							<Card.Title>{title}</Card.Title>
						</Card.Header>
						<Card.Content>
							<p>{description || "Sin descripción"}</p>
						</Card.Content>
					</Card>
				)
			})}
		</div>
	)
}