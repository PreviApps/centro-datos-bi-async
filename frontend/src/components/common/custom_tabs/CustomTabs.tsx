import { Tabs } from "@heroui/react";

export interface TabItem {
	id: string;
	label: string;
	content: React.ReactNode;
	isDisabled?: boolean;
	showSeparator?: boolean; // Controla si lleva separador antes de esta pestaña
}

interface CustomTabsProps {
	items: TabItem[];
	defaultSelectedKey?: string;
	selectedKey?: string;
	onSelectionChange?: (key: string) => void;
	variant?: "primary" | "secondary";
	orientation?: "horizontal" | "vertical";
	className?: string;
}

export function CustomTabs({
	items,
	defaultSelectedKey,
	selectedKey,
	onSelectionChange,
	variant = "primary",
	orientation = "horizontal",
	className = "w-full",
}: CustomTabsProps) {
	return (
		<Tabs
			variant={variant}
			orientation={orientation}
			className={className}
			defaultSelectedKey={defaultSelectedKey || items[0]?.id}
			selectedKey={selectedKey}
			onSelectionChange={(key) => onSelectionChange?.(key as string)}
		>
			{/* ListContainer maneja automáticamente el overflow con desvanecimientos y chevrons */}
			<Tabs.ListContainer>
				<Tabs.List aria-label="Gestión de permisos y configuraciones">
					{items.map((tab, index) => (
						<Tabs.Tab
							key={tab.id}
							id={tab.id}
							isDisabled={tab.isDisabled}
						>
							{/* Separador opcional (HeroUI indica que se pone a partir del segundo o según prefieras) */}
							{tab.showSeparator && index > 0 && <Tabs.Separator />}

							{tab.label}
							<Tabs.Indicator />
						</Tabs.Tab>
					))}
				</Tabs.List>
			</Tabs.ListContainer>

			{/* Renderizado dinámico de los paneles */}
			{items.map((tab) => (
				<Tabs.Panel key={tab.id} id={tab.id} className="pt-4">
					{tab.content}
				</Tabs.Panel>
			))}
		</Tabs>
	);
}