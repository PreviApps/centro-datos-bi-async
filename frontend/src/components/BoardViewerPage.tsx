import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PowerBIEmbed } from 'powerbi-client-react';
import { models } from 'powerbi-client';
import { getBoardEmbed } from '../api/boards';
import { ToastService } from '../utils/ToastService';
import CustomNavbar from './common/custom_navbar/CustomNavbar';
import CustomMainContent from './common/custom_main_content/CustomMainContent';
import { Button } from '@heroui/react';

export default function BoardViewerPage() {
	const { id } = useParams();
	const navigate = useNavigate();
	const [board, setBoard] = useState<any>(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		if (id) {
			loadBoardEmbedData(id);
		}
	}, [id]);

	async function loadBoardEmbedData(boardId: string) {
		setLoading(true);
		try {
			const data = await ToastService.execute({
				action: () => getBoardEmbed(boardId),
				loading: "Generando token de Power BI...",
				success: "Tablero listo",
				error: "No fue posible cargar la información de Power BI"
			});
			setBoard(data);
		} catch (error) {
			console.error("Error loading board embed info:", error);
		} finally {
			setLoading(false);
		}
	}

	if (loading) {
		return <div className="p-8 text-center">Cargando visor...</div>;
	}

	if (!board) {
		return (
			<div className="flex flex-col items-center justify-center h-screen text-center">
				<h3 className="text-lg font-semibold">Tablero no encontrado</h3>
				<Button className="mt-4" onPress={() => navigate(-1)}>Volver</Button>
			</div>
		);
	}

	const sanitizeEmbedUrl = (url: string) => {
		if (!url) return '';
		// Convierte http a https en producción
		return url.replace(/^http:\/\//i, 'https://');
	};

	/*return (
		<div className="flex flex-col h-screen overflow-hidden">
			{/*<CustomNavbar title={board.name}>
        <p>{board.description || "Visualización de Power BI"}</p>
      </CustomNavbar>}

			{/* Usamos un contenedor flex de altura completa sin min-h-screen forzado }
			<div className="flex-1 w-full bg-[#f3f4f6] text-gray-800 font-sans antialiased flex flex-col overflow-hidden">
				<main className="container mx-auto px-4 py-4 flex-1 flex flex-col overflow-hidden">
					<div className="flex justify-end mb-3 shrink-0">
						<Button
							variant="outline"
							onPress={() => navigate(-1)}
						>
							Regresar
						</Button>
					</div>

					{/* CONTENEDOR CON RELATIVE PARA QUE EL ESCUDO NO SE SALGA }
					<div className="flex-1 w-full bg-default-50 border border-default-200 rounded-xl overflow-hidden shadow-sm flex flex-col relative min-h-0">

						{/* ESCUDO TAPA-BARRA: Solo cubre el borde superior dentro de este cuadro }
						<div className="absolute top-0 left-0 w-full h-11 bg-default z-50 pointer-events-none" />
						{board.embed_url && board.embed_token ? (
							<PowerBIEmbed
								embedConfig={{
									type: 'report',
									id: board.powerbi_report_id,
									embedUrl: sanitizeEmbedUrl(board.embed_url),
									accessToken: board.embed_token,
									tokenType: models.TokenType.Embed,
									settings: {
										panes: {
											filters: { expanded: false, visible: false },
											pageNavigation: { visible: true },
										},
										bars: {
											statusBar: {
												visible: true, // Esto muestra la barra inferior con los botones de zoom y ajuste
											},
										},
										navContentPaneEnabled: true,
										background: models.BackgroundType.Transparent,
										layoutType: models.LayoutType.Custom,
										customLayout: {
											displayOption: models.DisplayOption.FitToWidth,
										},
									},
								}}
								cssClassName="w-full h-full"
								getEmbeddedComponent={(embeddedReport) => {
									console.log("Instancia del reporte:", embeddedReport);
								}}
							/>
						) : (
							<div className="flex items-center justify-center h-full text-red-500">
								Falta la URL de inserción o el token de acceso de Power BI.
							</div>
						)}
					</div>
				</main>
			</div>
		</div>
	);*/

	return (
    <div className="flex flex-col h-screen w-full overflow-hidden bg-[#f3f4f6]">
      {/*<CustomNavbar title={board.name}>
        <p>{board.description || "Visualización de Power BI"}</p>
      </CustomNavbar>*/}

      {/* Eliminamos "container mx-auto" y dejamos w-full fluido con flex-1 estrictos */}
      <div className="flex-1 w-full text-gray-800 font-sans antialiased flex flex-col overflow-hidden min-h-0 min-w-0 p-3 sm:p-4">
        
        {/* Botón superior */}
        <div className="flex justify-end mb-2 shrink-0">
          <Button
            variant="outline"
            onPress={() => navigate(-1)}
          >
            Regresar
          </Button>
        </div>

        {/* CONTENEDOR FLUIDO SIN SCROLLBARS */}
        <div className="flex-1 w-full bg-default-50 border border-default-200 rounded-xl overflow-hidden shadow-sm flex flex-col relative min-h-0 min-w-0">

          {/* ESCUDO TAPA-BARRA */}
          <div className="absolute top-0 left-0 w-full h-11 bg-default z-50 pointer-events-none" />

          {board.embed_url && board.embed_token ? (
            /* 
              Div wrapping que encapsula el iframe de Power BI a las dimensiones exactas 
              del espacio visible sin provocar desbordamiento.
            */
            <div className="w-full h-full flex-1 min-h-0 min-w-0 [&>div]:h-full [&>div]:w-full [&>iframe]:h-full [&>iframe]:w-full [&>iframe]:border-none">
              <PowerBIEmbed
                embedConfig={{
                  type: 'report',
                  id: board.powerbi_report_id,
                  embedUrl: sanitizeEmbedUrl(board.embed_url),
                  accessToken: board.embed_token,
                  tokenType: models.TokenType.Embed,
                  settings: {
                    panes: {
                      filters: { expanded: false, visible: false },
                      pageNavigation: { visible: true },
                    },
                    bars: {
                      statusBar: {
                        visible: true,
                      },
                    },
                    navContentPaneEnabled: true,
                    background: models.BackgroundType.Transparent,
                    layoutType: models.LayoutType.Custom,
                    customLayout: {
                      // Escala todo el lienzo (ancho y alto) dentro del espacio visible exacto
                      displayOption: models.DisplayOption.FitToPage,
                    },
                  },
                }}
                cssClassName="w-full h-full"
                getEmbeddedComponent={(embeddedReport) => {
                  console.log("Instancia del reporte:", embeddedReport);
                }}
              />
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-red-500">
              Falta la URL de inserción o el token de acceso de Power BI.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}