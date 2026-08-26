import { Check } from "@gravity-ui/icons";
import { Button, Form, TextField } from "@heroui/react";
import { FormEvent, ReactNode } from "react";

interface FormProps{
	children: ReactNode,
	onSubmit?: (e: FormEvent) => void;
}

export function CustomForm({children, onSubmit}: FormProps) {
	return (
		<Form className="flex flex-col gap-5" onSubmit={onSubmit}>
			{children}
			<div className="flex gap-2">
				<Button type="submit">
					<Check />
					Submit
				</Button>
				<Button type="reset" variant="secondary">
					Reset
				</Button>
			</div>
		</Form>
	)
}