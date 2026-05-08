import xml.etree.ElementTree as ET

def create_drawio(filename, title, classes_config, edges_config):
    mxfile = ET.Element("mxfile", host="Electron", modified="2023-11-01T00:00:00.000Z", agent="Mozilla/5.0", version="22.0.8", type="device")
    diagram = ET.SubElement(mxfile, "diagram", id="diagram_" + title.replace(" ", "_"), name=title)
    mxGraphModel = ET.SubElement(diagram, "mxGraphModel", dx="1000", dy="1000", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="1169", pageHeight="827", math="0", shadow="0")
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

    def add_edge(parent_id, source_id, target_id, style, label=""):
        nonlocal cell_id
        cell = ET.SubElement(root, "mxCell", id=str(cell_id), value=label, style=style, edge="1", parent=str(parent_id), source=str(source_id), target=str(target_id))
        ET.SubElement(cell, "mxGeometry", relative="1", **{"as": "geometry"})
        cell_id += 1
        return cell_id - 1

    # Tiers
    tier1_style = "swimlane;horizontal=0;whiteSpace=wrap;html=1;fillColor=#E6E6FA;strokeColor=#B0C4DE;fontStyle=1;startSize=40;fontSize=14;"
    tier2_style = "swimlane;horizontal=0;whiteSpace=wrap;html=1;fillColor=#F0FFF0;strokeColor=#8FBC8F;fontStyle=1;startSize=40;fontSize=14;"
    tier3_style = "swimlane;horizontal=0;whiteSpace=wrap;html=1;fillColor=#FFF8DC;strokeColor=#DEB887;fontStyle=1;startSize=40;fontSize=14;"
    
    t1_id = add_cell(1, "TẦNG 1: UI / VIEW", tier1_style, 40, 40, 1100, 240)
    t2_id = add_cell(1, "TẦNG 2: CONTROLLER", tier2_style, 40, 300, 1100, 240)
    t3_id = add_cell(1, "TẦNG 3: MODEL / ENTITY", tier3_style, 40, 560, 1100, 280)

    def build_class_html(name, fields, methods):
        html = f"<p style='margin:0px;margin-top:4px;text-align:center;'><b>{name}</b></p><hr size='1'/>"
        if fields:
            html += f"<p style='margin:0px;margin-left:4px;'>" + "<br>".join(fields) + "</p><hr size='1'/>"
        else:
            html += f"<hr size='1'/>"
        if methods:
            html += f"<p style='margin:0px;margin-left:4px;'>" + "<br>".join(methods) + "</p>"
        return html

    nodes = {}
    
    for cls in classes_config:
        tier = cls["tier"]
        parent_id = t1_id if tier == 1 else (t2_id if tier == 2 else t3_id)
        color = "#DCDCDC" if tier == 1 else ("#C1FFC1" if tier == 2 else "#FFE4B5")
        html_val = build_class_html(cls["name"], cls.get("fields", []), cls.get("methods", []))
        style = f"verticalAlign=top;align=left;overflow=fill;fontSize=12;fontFamily=Helvetica;html=1;whiteSpace=wrap;fillColor={color};"
        nodes[cls["name"]] = add_cell(parent_id, html_val, style, cls["x"], cls["y"], cls["w"], cls["h"])

    edge_dependency = "endArrow=classic;html=1;edgeStyle=orthogonalEdgeStyle;dashed=1;"
    edge_association = "endArrow=none;html=1;edgeStyle=orthogonalEdgeStyle;"
    edge_directed_assoc = "endArrow=classic;html=1;edgeStyle=orthogonalEdgeStyle;"
    edge_composition = "endArrow=none;html=1;edgeStyle=orthogonalEdgeStyle;startArrow=diamond;startFill=1;"

    for edge in edges_config:
        s_id = nodes.get(edge["src"])
        t_id = nodes.get(edge["tgt"])
        if s_id and t_id:
            style = edge_dependency
            if edge["type"] == "composition": style = edge_composition
            elif edge["type"] == "directed_assoc": style = edge_directed_assoc
            elif edge["type"] == "association": style = edge_association
            
            # Place edges in the root (1) unless specified
            add_edge(1, s_id, t_id, style, edge.get("label", ""))

    xml_str = ET.tostring(mxfile, encoding="unicode", xml_declaration=False)
    with open(f"../Docs/Design/Bieu do/{filename}", "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(xml_str)

# Common classes
m_nguoidung = {"tier": 3, "name": "NguoiDung", "fields": ["- user_id", "- username", "- role", "- email", "- password_hash"], "methods": ["+ save()", "+ delete()"], "x": 60, "y": 40, "w": 180, "h": 140}
m_phonghoc = {"tier": 3, "name": "PhongHoc", "fields": ["- room_id", "- name", "- capacity", "- status"], "methods": ["+ save()", "+ delete()"], "x": 300, "y": 40, "w": 180, "h": 120}

# --- FILE 1: QUẢN LÝ PHÒNG ---
classes_1 = [
    {"tier": 1, "name": "UI_NguoiDung (UC)", "fields": [], "methods": ["+ hien_thi()", "+ cap_nhat()"], "x": 60, "y": 40, "w": 180, "h": 80},
    {"tier": 1, "name": "UI_PhongHoc (UC)", "fields": [], "methods": ["+ hien_thi()", "+ cap_nhat()"], "x": 300, "y": 40, "w": 180, "h": 80},
    {"tier": 1, "name": "UI_ThietBi (UC)", "fields": [], "methods": ["+ hien_thi()", "+ cap_nhat()"], "x": 540, "y": 40, "w": 180, "h": 80},
    
    {"tier": 2, "name": "DieuKhienXacThuc", "fields": ["- user_dao"], "methods": ["+ authenticate()"], "x": 60, "y": 40, "w": 180, "h": 80},
    {"tier": 2, "name": "DieuKhienNguoiDung", "fields": ["- user_dao"], "methods": ["+ list_users()", "+ save()"], "x": 60, "y": 140, "w": 180, "h": 80},
    {"tier": 2, "name": "DieuKhienPhong", "fields": ["- room_dao"], "methods": ["+ list_rooms()", "+ save()"], "x": 300, "y": 40, "w": 180, "h": 80},
    {"tier": 2, "name": "DieuKhienThietBi", "fields": ["- equip_dao"], "methods": ["+ list_equip()", "+ save()"], "x": 540, "y": 40, "w": 180, "h": 80},
    
    m_nguoidung,
    m_phonghoc,
    {"tier": 3, "name": "ThietBi", "fields": ["- equip_id", "- name", "- room_id"], "methods": ["+ save()", "+ delete()"], "x": 540, "y": 40, "w": 180, "h": 100},
]
edges_1 = [
    {"src": "UI_NguoiDung (UC)", "tgt": "DieuKhienNguoiDung", "type": "dependency"},
    {"src": "UI_NguoiDung (UC)", "tgt": "DieuKhienXacThuc", "type": "dependency"},
    {"src": "UI_PhongHoc (UC)", "tgt": "DieuKhienPhong", "type": "dependency"},
    {"src": "UI_ThietBi (UC)", "tgt": "DieuKhienThietBi", "type": "dependency"},
    {"src": "DieuKhienNguoiDung", "tgt": "NguoiDung", "type": "dependency"},
    {"src": "DieuKhienXacThuc", "tgt": "NguoiDung", "type": "dependency"},
    {"src": "DieuKhienPhong", "tgt": "PhongHoc", "type": "dependency"},
    {"src": "DieuKhienThietBi", "tgt": "ThietBi", "type": "dependency"},
    {"src": "PhongHoc", "tgt": "ThietBi", "type": "composition", "label": "1  *"}
]
create_drawio("1_QuanLyPhong_3Tier.drawio", "Quản Lý Phòng", classes_1, edges_1)

# --- FILE 2: ĐẶT PHÒNG & SỰ CỐ ---
classes_2 = [
    {"tier": 1, "name": "UI_DatPhong (UC)", "fields": [], "methods": ["+ hien_thi()", "+ dat_phong()"], "x": 60, "y": 40, "w": 180, "h": 80},
    {"tier": 1, "name": "UI_SuCoPhong (UC)", "fields": [], "methods": ["+ hien_thi()", "+ bao_cao()"], "x": 300, "y": 40, "w": 180, "h": 80},
    {"tier": 1, "name": "UI_LichPhong (UC)", "fields": [], "methods": ["+ hien_thi()", "+ xem_lich()"], "x": 540, "y": 40, "w": 180, "h": 80},
    
    {"tier": 2, "name": "DieuKhienDatPhong", "fields": ["- booking_dao"], "methods": ["+ create_booking()"], "x": 60, "y": 40, "w": 180, "h": 80},
    {"tier": 2, "name": "DieuKhienLich", "fields": ["- schedule_dao"], "methods": ["+ list_schedule()"], "x": 540, "y": 40, "w": 180, "h": 80},
    {"tier": 2, "name": "DieuKhienBaoCao", "fields": ["- room_ctrl", "- booking_ctrl"], "methods": ["+ dashboard()"], "x": 300, "y": 40, "w": 180, "h": 80},
    
    {"tier": 3, "name": "DatPhong", "fields": ["- booking_id", "- user_id", "- room_id"], "methods": ["+ save()", "+ delete()"], "x": 60, "y": 40, "w": 180, "h": 100},
    {"tier": 3, "name": "SuCoPhong", "fields": ["- issue_id", "- room_id", "- user_id"], "methods": ["+ save()", "+ update()"], "x": 300, "y": 40, "w": 180, "h": 100},
    {"tier": 3, "name": "LichPhong", "fields": ["- room_id", "- slot", "- status"], "methods": ["+ save()", "+ delete()"], "x": 540, "y": 40, "w": 180, "h": 100},
    {"tier": 3, "name": "PhongHoc", "fields": ["- room_id", "- name"], "methods": [], "x": 800, "y": 40, "w": 120, "h": 80},
    {"tier": 3, "name": "NguoiDung", "fields": ["- user_id", "- name"], "methods": [], "x": 800, "y": 140, "w": 120, "h": 80},
]
edges_2 = [
    {"src": "UI_DatPhong (UC)", "tgt": "DieuKhienDatPhong", "type": "dependency"},
    {"src": "UI_LichPhong (UC)", "tgt": "DieuKhienLich", "type": "dependency"},
    {"src": "DieuKhienDatPhong", "tgt": "DatPhong", "type": "dependency"},
    {"src": "DieuKhienLich", "tgt": "LichPhong", "type": "dependency"},
    {"src": "PhongHoc", "tgt": "LichPhong", "type": "composition", "label": "1  *"},
    {"src": "PhongHoc", "tgt": "DatPhong", "type": "directed_assoc", "label": "1  *"},
    {"src": "NguoiDung", "tgt": "DatPhong", "type": "directed_assoc", "label": "1  *"},
    {"src": "PhongHoc", "tgt": "SuCoPhong", "type": "directed_assoc", "label": "1  *"},
    {"src": "NguoiDung", "tgt": "SuCoPhong", "type": "directed_assoc", "label": "1  *"}
]
create_drawio("2_DatPhong_SuCo_3Tier.drawio", "Đặt Phòng & Sự Cố", classes_2, edges_2)

# --- FILE 3: ĐÁNH GIÁ & THÔNG BÁO ---
classes_3 = [
    {"tier": 1, "name": "UI_DanhGiaPhong (UC)", "fields": [], "methods": ["+ hien_thi()", "+ gui_danh_gia()"], "x": 60, "y": 40, "w": 200, "h": 80},
    {"tier": 1, "name": "UI_ThongBao (UC)", "fields": [], "methods": ["+ hien_thi()", "+ xem_thong_bao()"], "x": 300, "y": 40, "w": 200, "h": 80},
    
    {"tier": 2, "name": "DieuKhienPhanHoiPhong", "fields": ["- rating_dao"], "methods": ["+ add_rating()", "+ avg_stars()"], "x": 60, "y": 40, "w": 200, "h": 80},
    
    {"tier": 3, "name": "DanhGiaPhong", "fields": ["- id", "- room_id", "- user_id", "- rating"], "methods": ["+ add()", "+ average()"], "x": 60, "y": 40, "w": 200, "h": 100},
    {"tier": 3, "name": "ThongBao", "fields": ["- notif_id", "- user_id", "- message"], "methods": ["+ send()", "+ read()"], "x": 300, "y": 40, "w": 200, "h": 100},
    {"tier": 3, "name": "PhongHoc", "fields": ["- room_id"], "methods": [], "x": 550, "y": 40, "w": 120, "h": 60},
    {"tier": 3, "name": "NguoiDung", "fields": ["- user_id"], "methods": [], "x": 550, "y": 120, "w": 120, "h": 60},
]
edges_3 = [
    {"src": "UI_DanhGiaPhong (UC)", "tgt": "DieuKhienPhanHoiPhong", "type": "dependency"},
    {"src": "DieuKhienPhanHoiPhong", "tgt": "DanhGiaPhong", "type": "dependency"},
    {"src": "PhongHoc", "tgt": "DanhGiaPhong", "type": "directed_assoc", "label": "1  *"},
    {"src": "NguoiDung", "tgt": "DanhGiaPhong", "type": "directed_assoc", "label": "1  *"},
    {"src": "NguoiDung", "tgt": "ThongBao", "type": "directed_assoc", "label": "1  *"}
]
create_drawio("3_DanhGia_ThongBao_3Tier.drawio", "Đánh Giá & Thông Báo", classes_3, edges_3)

