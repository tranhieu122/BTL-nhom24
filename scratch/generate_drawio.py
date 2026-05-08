import xml.etree.ElementTree as ET
import urllib.parse

def create_drawio():
    mxfile = ET.Element("mxfile", host="Electron", modified="2023-11-01T00:00:00.000Z", agent="Mozilla/5.0", version="22.0.8", type="device")
    diagram = ET.SubElement(mxfile, "diagram", id="3tier_diagram", name="3-Tier Architecture")
    mxGraphModel = ET.SubElement(diagram, "mxGraphModel", dx="1000", dy="1000", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="827", pageHeight="1169", math="0", shadow="0")
    root = ET.SubElement(mxGraphModel, "root")
    
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")
    
    cell_id = 2
    
    def add_cell(parent_id, value, style, x, y, width, height):
        nonlocal cell_id
        cell = ET.SubElement(root, "mxCell", id=str(cell_id), value=value, style=style, vertex="1", parent=str(parent_id))
        ET.SubElement(cell, "mxGeometry", x=str(x), y=str(y), width=str(width), height=str(height), **{"as": "geometry"})
        cell_id += 1
        return cell_id - 1

    def add_edge(parent_id, source_id, target_id, style):
        nonlocal cell_id
        cell = ET.SubElement(root, "mxCell", id=str(cell_id), style=style, edge="1", parent=str(parent_id), source=str(source_id), target=str(target_id))
        ET.SubElement(cell, "mxGeometry", relative="1", **{"as": "geometry"})
        cell_id += 1
        return cell_id - 1

    # Tiers
    tier1_style = "swimlane;horizontal=0;whiteSpace=wrap;html=1;fillColor=#E6E6FA;strokeColor=#B0C4DE;fontStyle=1;startSize=40;"
    tier2_style = "swimlane;horizontal=0;whiteSpace=wrap;html=1;fillColor=#F0FFF0;strokeColor=#8FBC8F;fontStyle=1;startSize=40;"
    tier3_style = "swimlane;horizontal=0;whiteSpace=wrap;html=1;fillColor=#FFF8DC;strokeColor=#DEB887;fontStyle=1;startSize=40;"
    
    t1_id = add_cell(1, "TẦNG 1: PRESENTATION LAYER (UI / CONTROLLER)", tier1_style, 40, 40, 760, 240)
    t2_id = add_cell(1, "TẦNG 2: BUSINESS LOGIC LAYER (CLASS / SERVICE)", tier2_style, 40, 320, 760, 240)
    t3_id = add_cell(1, "TẦNG 3: DATA LAYER (ENTITY / TABLE)", tier3_style, 40, 600, 760, 240)
    
    # Arrows between tiers
    edge_style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0.5;entryY=1;entryDx=0;entryDy=0;exitX=0.5;exitY=0;exitDx=0;exitDy=0;"
    add_edge(1, t2_id, t1_id, edge_style)
    add_edge(1, t3_id, t2_id, edge_style)

    # Groups in Tier 1
    group_style = "swimlane;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#D3D3D3;startSize=23;fontSize=11;"
    item_style_t1 = "rounded=1;whiteSpace=wrap;html=1;fillColor=#DCDCDC;strokeColor=#A9A9A9;fontSize=12;"
    
    g1_1 = add_cell(t1_id, "Quản lý phòng", group_style, 60, 20, 200, 180)
    add_cell(g1_1, "NguoiDung (UC)", item_style_t1, 20, 40, 160, 30)
    add_cell(g1_1, "PhongHoc (UC)", item_style_t1, 20, 80, 160, 30)
    add_cell(g1_1, "ThietBi (UC)", item_style_t1, 20, 120, 160, 30)
    
    g1_2 = add_cell(t1_id, "Đặt phòng / Sự cố", group_style, 280, 20, 200, 180)
    add_cell(g1_2, "DatPhong (UC)", item_style_t1, 20, 40, 160, 30)
    add_cell(g1_2, "SuCoPhong (UC)", item_style_t1, 20, 80, 160, 30)
    add_cell(g1_2, "LichPhong (UC)", item_style_t1, 20, 120, 160, 30)
    
    g1_3 = add_cell(t1_id, "Đánh giá / Thông báo", group_style, 500, 20, 200, 180)
    add_cell(g1_3, "DanhGiaPhong (UC)", item_style_t1, 20, 40, 160, 30)
    
    # Groups in Tier 2
    item_style_t2 = "rounded=1;whiteSpace=wrap;html=1;fillColor=#C1FFC1;strokeColor=#8FBC8F;fontSize=12;"
    
    g2_1 = add_cell(t2_id, "Xác thực & người dùng", group_style, 60, 20, 200, 100)
    add_cell(g2_1, "DieuKhienXacThuc", item_style_t2, 20, 30, 160, 25)
    add_cell(g2_1, "DieuKhienNguoiDung", item_style_t2, 20, 65, 160, 25)
    
    g2_2 = add_cell(t2_id, "Phòng & thiết bị", group_style, 280, 20, 200, 100)
    add_cell(g2_2, "DieuKhienPhong", item_style_t2, 20, 30, 160, 25)
    add_cell(g2_2, "DieuKhienThietBi", item_style_t2, 20, 65, 160, 25)
    
    g2_3 = add_cell(t2_id, "Đặt phòng & lịch", group_style, 500, 20, 200, 100)
    add_cell(g2_3, "DieuKhienDatPhong", item_style_t2, 20, 30, 160, 25)
    add_cell(g2_3, "DieuKhienLich", item_style_t2, 20, 65, 160, 25)
    
    g2_4 = add_cell(t2_id, "Báo cáo & phản hồi", group_style, 60, 130, 420, 80)
    add_cell(g2_4, "DieuKhienBaoCao", item_style_t2, 20, 35, 160, 25)
    add_cell(g2_4, "DieuKhienPhanHoiPhong", item_style_t2, 200, 35, 160, 25)

    # Groups in Tier 3
    item_style_t3 = "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFE4B5;strokeColor=#DEB887;fontSize=12;"
    
    g3_1 = add_cell(t3_id, "Bảng người dùng", group_style, 60, 20, 200, 180)
    add_cell(g3_1, "users", item_style_t3, 20, 40, 160, 30)
    
    g3_2 = add_cell(t3_id, "Bảng phòng & thiết bị", group_style, 280, 20, 200, 180)
    add_cell(g3_2, "Phong Hoc", item_style_t3, 20, 40, 160, 30)
    add_cell(g3_2, "Thiet bi", item_style_t3, 20, 80, 160, 30)
    add_cell(g3_2, "Lich phong", item_style_t3, 20, 120, 160, 30)
    
    g3_3 = add_cell(t3_id, "Bảng nghiệp vụ", group_style, 500, 20, 240, 180)
    add_cell(g3_3, "Dat Phong", item_style_t3, 20, 40, 90, 30)
    add_cell(g3_3, "Danh gia phong", item_style_t3, 130, 40, 90, 30)
    add_cell(g3_3, "room_issues", item_style_t3, 20, 80, 90, 30)
    add_cell(g3_3, "Thong bao", item_style_t3, 130, 80, 90, 30)

    xml_str = ET.tostring(mxfile, encoding="unicode", xml_declaration=False)
    # the drawing needs to be unescaped html if we used it, but we didn't.
    with open("../Docs/Design/Bieu do/MoHinh3Tier.drawio", "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(xml_str)

create_drawio()
