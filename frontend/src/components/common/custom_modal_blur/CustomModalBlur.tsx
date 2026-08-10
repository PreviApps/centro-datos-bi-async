import { Modal } from "@heroui/react"
import { ReactNode } from "react"

interface BaseModalProps {
    isOpen: boolean
    onOpenChange: (open: boolean) => void
    children: ReactNode
}

export function CustomModalBlur({isOpen, onOpenChange, children}: BaseModalProps){
    return(
        <>
					<Modal isOpen={isOpen} onOpenChange={onOpenChange}>
						<Modal.Backdrop variant="blur">
							<Modal.Container>
								<Modal.Dialog>
									{children}
								</Modal.Dialog>
							</Modal.Container>
						</Modal.Backdrop>
					</Modal>
        </>
    )
}