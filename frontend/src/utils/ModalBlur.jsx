import { useState, useEffect } from "react";
import {
  Modal,
  Button,
  Input,
  CloseButton,
  TextArea,
} from "@heroui/react";
import { Xmark } from "@gravity-ui/icons";
import { CustomModalBlur } from "../components/common/custom_modal_blur/CustomModalBlur";

export function SaveQueryModal({
  open,
  onOpenChange,
  query,
  onSave,
  reportData,
  setReportData,
  canSave
}) {

  const handleSubmit = () => {
    const matches = query.matchAll(
      /@\(([a-zA-Z0-9_]+):(string|date|number|boolean)\)/g
    );

    const parameters = [...matches].map(match => ({
      name: match[1],
      type: match[2],
      required: false,
      default: null,
    }));

    onSave({
      ...reportData,
      sql_template: query,
      parameters
    });

    onOpenChange(false);
  };

  return (
    <CustomModalBlur
      isOpen={open}
      onOpenChange={onOpenChange}
    >
      <Modal.Dialog className="sm:max-w-[500px]">
        <div className="absolute right-4 top-4 z-10">
          <Button
            isIconOnly
            variant="light"
            onPress={() => onOpenChange(false)}
          >
            <Xmark />
          </Button>
        </div>

        <Modal.Header>
          <Modal.Heading>
            {reportData?.id ? "Editar reporte" : "Guardar reporte"}
          </Modal.Heading>
        </Modal.Header>

        <Modal.Body>
          <div className="space-y-4">
            <Input
              label="Query Name"
              placeholder="My awesome query"
              value={reportData?.name ?? "Reporte nuevo"}
              onChange={(e) =>
                setReportData(prev => ({
                  ...prev,
                  name: e.target.value
                }))
              }
            />

            <div>
              <label className="mb-2 block text-sm font-medium">
                SQL Preview
              </label>

              <pre className="max-h-48 overflow-auto rounded-md bg-default-100 p-3 text-xs">
                {query}
              </pre>
            </div>
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium">
              SQL Description
            </label>
          </div>

        </Modal.Body>

        <TextArea
          label="Query Description"
          placeholder="This query request facturation data"
          value={reportData?.description ?? "Reporte nuevo"}
          onChange={(e) =>
            setReportData(prev => ({
              ...prev,
              description: e.target.value
            }))
          }
        />

        <Modal.Footer>
          <Button
            variant="bordered"
            onPress={() => onOpenChange(false)}
          >
            Cancel
          </Button>

          <Button
            color="primary"
            onPress={handleSubmit}
            isDisabled={!canSave}
          >
            {reportData?.id ? 'Actualizar' : 'Guardar'}
          </Button>
        </Modal.Footer>
      </Modal.Dialog>
    </CustomModalBlur>
  )
}