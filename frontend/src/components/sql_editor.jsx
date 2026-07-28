import React, { useState, useEffect, useMemo } from "react";
import Editor, { loader } from "@monaco-editor/react";
import * as monaco from "monaco-editor";
import { listTables } from "../api/tables";
import { executeQuery, saveQuery } from "../api/query_service";
import { FloppyDisk, ThunderboltFill } from "@gravity-ui/icons";
import { Button, Tooltip, toast } from "@heroui/react";
import { ToastService } from "../utils/ToastService";
import { SaveQueryModal } from "../utils/ModalBlur";
import { pollJob } from "../utils/polljob";
import { getJob } from "../api/jobs";
import { updateReport } from "../api/reports";
import { useNavigate } from "react-router-dom";

loader.init().then((monacoInstance) => {
  monacoInstance.languages.register({ id: "sql" });
});

function SqlEditor({ setSqlPreview, setIsQueryLoading, initialValue = '', reportToEdit = null }) {
  const [query, setQuery] = useState("");
  const [currentPath, setCurrentPath] = useState(""); // path actual del MinIO
  const [sqlError, setSqlError] = useState(null);
  const [isSaveModalOpen, setIsSaveModalOpen] = useState(false);
  const [reportData, setReportData] = useState({
    name: "",
    description: "",
    parquet_path: "",
    created_by: ""
  })
  const initialReport = useMemo(() => ({
    name: reportToEdit?.name ?? "",
    description: reportToEdit?.description ?? "",
    sql_template: initialValue ?? ""
  }), [reportToEdit, initialValue]);

  const navigate = useNavigate();

  useEffect(() => {
    if (initialValue) {
      setQuery(initialValue);
    }

    if (reportToEdit) {
      setReportData({
        id: reportToEdit.id,
        name: reportToEdit.name || "",
        description: reportToEdit.description || "",
        parquet_path: reportToEdit.parquet_path || "",
        created_by: reportToEdit.created_by || ""
      });
    }

  }, [initialValue, reportToEdit]);

  useEffect(() => {
    loader.init().then((monacoInstance) => {
      const provider = monacoInstance.languages.registerCompletionItemProvider(
        "sql",
        {
          triggerCharacters: ["'", "/", ".", " ", ":"],
          provideCompletionItems: async (model, position) => {

            const line =
              model.getLineContent(position.lineNumber);

            const textUntilCursor =
              line.slice(0, position.column - 1);

            const typeMatch =
              textUntilCursor.match(
                /@\([a-zA-Z0-9_]+:([a-zA-Z]*)$/
              );

            if (typeMatch) {

              const types = [
                "string",
                "date",
                "number",
                "boolean"
              ];

              return {
                suggestions: types.map((type) => ({
                  label: type,

                  kind:
                    monaco.languages.CompletionItemKind.Enum,

                  insertText: `${type})`,
                })),
              };
            }

            // Detectar read_parquet('...')
            const parquetMatch = textUntilCursor.match(
              /read_parquet\(['"]([^'"]*)$/
            );

            if (!parquetMatch) {
              return { suggestions: [] };
            }

            const partialPath = parquetMatch[1];

            try {

              const res = await listTables(partialPath);

              const items = res.items ?? [];

              const suggestions = items.map((item) => {

                const fullPath = item.object_name;

                const label =
                  fullPath.replace(partialPath, "");

                return {
                  label,

                  kind: item.object_name.endsWith("/")
                    ? monaco.languages.CompletionItemKind.Folder
                    : monaco.languages.CompletionItemKind.File,

                  insertText: label,
                };
              });

              return { suggestions };

            } catch (err) {

              console.error(err);

              return { suggestions: [] };
            }
          },
        }
      );

      return () => provider.dispose();
    });
  }, [currentPath]);

  const handleExecute = async () => {
    try {
      setSqlError(null)
      setIsQueryLoading?.(true)
      const response = await executeQuery(query);

      console.log("JOB BIEN PREVIEW", response)

      const jobId = response.job_id;

      if (!jobId) {
        throw new Error("No se recibió job desde el backend")
      }

      const finalJob = await pollJob(
        () => getJob(jobId),
        job => job.status === "success" || job.status === "failed",
        {
          interval: 1500,
          timeout: 1000 * 60 * 3
        }
      );

      if (finalJob.status === "success") {
        setSqlPreview(finalJob.preview_results);
      } else {
        throw new Error(finalJob.error);
      }
    } catch (err) {
      setSqlError(
        err?.message || "Error ejecutando query"
      );
    } finally {
      setIsQueryLoading?.(false);
    }
  };

  const handleSaveQuery = () => {
    setIsSaveModalOpen(true)
  };

  const handleEdit = (payload) => {

    const isEditing = Boolean(reportToEdit?.id);

    ToastService.execute({
      action: () => isEditing ? updateReport(reportToEdit.id, payload) : saveQuery(payload),
      loading: isEditing ? 'Actualizando reporte...' : "Saving query...",
      //success: isEditing? 'Reporte actualizado con éxito' : "Query saved successfully",
      success: () => {
        setIsSaveModalOpen(false);
        navigate('/reports', { replace: true })
        return isEditing
          ? "Reporte actualizado"
          : "Reporte creado";
      },
      error: (err) => err instanceof Error ? err.message : String(err)
    });
  }

  const isEditing = Boolean(reportToEdit?.id);

  const hasChanges = isEditing
    ? (
      initialReport &&
      (
        initialReport.name !== reportData.name ||
        initialReport.description !== reportData.description ||
        initialReport.sql_template !== query
      )
    )
    : query.trim().length > 10;

  return (
    <div style={{ padding: "20px" }}>
      <Editor
        height="300px"
        defaultLanguage="sql"
        value={query}
        onChange={(value) => setQuery(value || "")}
        options={{
          fontSize: 14,
          minimap: { enabled: false },
          wordWrap: "on",
          automaticLayout: true,
          quickSuggestions: true,
          suggestOnTriggerCharacters: true,
        }}
      />
      <div style={{ marginTop: "10px" }}>

        <Tooltip delay={0}>
          <Button onClick={handleExecute} isIconOnly variant="ghost">
            <ThunderboltFill />
          </Button>
          <Tooltip.Content>
            <p>Execute Query (Limit 20)</p>
          </Tooltip.Content>
        </Tooltip>
        <Tooltip delay={0}>
          <Button onClick={handleSaveQuery} isIconOnly variant="ghost" isDisabled={!hasChanges}>
            <FloppyDisk />
          </Button>
          <Tooltip.Content>
            <p>Save Query</p>
          </Tooltip.Content>
        </Tooltip>
        <SaveQueryModal
          open={isSaveModalOpen}
          onOpenChange={setIsSaveModalOpen}
          query={query}
          onSave={handleEdit}
          reportData={reportData}
          setReportData={setReportData}
          canSave={hasChanges}
        />
      </div>
      {sqlError && (
        <div
          style={{
            marginTop: "10px",
            padding: "12px",
            background: "#2b0000",
            color: "#ffb3b3",
            border: "1px solid red",
            whiteSpace: "pre-wrap",
            fontFamily: "monospace"
          }}
        >
          {sqlError}
        </div>
      )}
    </div>
  );
}

export default SqlEditor;