import xml.etree.ElementTree as ET

def create_full_drawio():
    mxfile = ET.Element("mxfile", host="Electron", modified="2023-11-01T00:00:00.000Z", agent="Mozilla/5.0", version="22.0.8", type="device")
    diagram = ET.SubElement(mxfile, "diagram", id="3tier_class_diagram", name="3-Tier Class Diagram")
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
    
    # Let's make it wide
    t1_id = add_cell(1, "TẦNG 1: PRESENTATION LAYER (UI / VIEW)", tier1_style, 40, 40, 1600, 300)
    t2_id = add_cell(1, "TẦNG 2: BUSINESS LOGIC LAYER (CONTROLLER)", tier2_style, 40, 360, 1600, 340)
    t3_id = add_cell(1, "TẦNG 3: DATA LAYER (MODEL / ENTITY)", tier3_style, 40, 720, 1600, 340)

    # Class Generator
    def build_class_html(name, fields, methods, color):
        html = f"<p style='margin:0px;margin-top:4px;text-align:center;'><b>{name}</b></p><hr size='1'/>"
        if fields:
            html += f"<p style='margin:0px;margin-left:4px;'>" + "<br>".join(fields) + "</p><hr size='1'/>"
        else:
            html += f"<hr size='1'/>"
        if methods:
            html += f"<p style='margin:0px;margin-left:4px;'>" + "<br>".join(methods) + "</p>"
        return html

    def add_class(parent_id, name, fields, methods, color, x, y, w, h):
        html_val = build_class_html(name, fields, methods, color)
        # We must escape the html text inside value implicitly by ElementTree, but for draw.io html=1 is needed in style
        style = f"verticalAlign=top;align=left;overflow=fill;fontSize=12;fontFamily=Helvetica;html=1;whiteSpace=wrap;fillColor={color};"
        return add_cell(parent_id, html_val, style, x, y, w, h)

    nodes = {}
    
    # ==== TIER 3: MODELS ====
    color_t3 = "#FFE4B5"
    m_nguoidung = add_class(t3_id, "NguoiDung", [
        "- user_id: str", "- username: str", "- full_name: str", "- role: str", 
        "- email: str", "- phone: str", "- password_hash: str", "- status: str"
    ], [
        "+ list_all(): list", "+ find_by_id(id)", "+ find_by_username(u)", 
        "+ find_by_email(e)", "+ save(user)", "+ delete(id)"
    ], color_t3, 100, 40, 200, 260)
    nodes['NguoiDung'] = m_nguoidung

    m_phonghoc = add_class(t3_id, "PhongHoc", [
        "- room_id: str", "- name: str", "- capacity: int", 
        "- room_type: str", "- equipment: str", "- status: str"
    ], [
        "+ list_all(): list", "+ find_by_id(id)", 
        "+ save(room)", "+ delete(id)"
    ], color_t3, 450, 40, 200, 180)
    nodes['PhongHoc'] = m_phonghoc

    m_thietbi = add_class(t3_id, "ThietBi", [
        "- equipment_id: str", "- name: str", "- equipment_type: str", 
        "- room_id: str", "- status: str", "- purchase_date: str"
    ], [
        "+ list_all(): list", "+ list_by_room(id)", 
        "+ find_by_id(id)", "+ save(equip)", "+ delete()"
    ], color_t3, 450, 240, 200, 160)
    nodes['ThietBi'] = m_thietbi

    m_lichphong = add_class(t3_id, "LichPhong", [
        "- room_id: str", "- weekday: str", "- slot: str", "- status: str"
    ], [
        "+ list_by_room(id)", "+ save_schedule()", 
        "+ delete(id, slot)", "+ clear_room(id)"
    ], color_t3, 700, 240, 180, 140)
    nodes['LichPhong'] = m_lichphong

    m_datphong = add_class(t3_id, "DatPhong", [
        "- booking_id: str", "- user_id: str", "- room_id: str", 
        "- date: str", "- slot: str", "- purpose: str", "- status: str"
    ], [
        "+ list_all(): list", "+ find_by_id(id)", 
        "+ find_by_user(id)", "+ save(booking)", "+ delete(id)"
    ], color_t3, 920, 40, 200, 200)
    nodes['DatPhong'] = m_datphong

    m_danhgiaphong = add_class(t3_id, "DanhGiaPhong", [
        "- id: int", "- room_id: str", "- user_id: str", "- user_name: str", 
        "- rating: int", "- comment: str", "- created_at: str"
    ], [
        "+ add(room_id, user_name, ...)", "+ list_by_room(id)", "+ average_stars(id)"
    ], color_t3, 1150, 40, 220, 160)
    nodes['DanhGiaPhong'] = m_danhgiaphong

    m_sucophong = add_class(t3_id, "SuCoPhong", [
        "- id: int", "- room_id: str", "- user_id: str", "- user_name: str", 
        "- description: str", "- status: str", "- notes: str", "- created_at: str"
    ], [
        "+ report(room, user, desc)", "+ list_all()", "+ update_status(id, stat)"
    ], color_t3, 1150, 220, 220, 160)
    nodes['SuCoPhong'] = m_sucophong

    # ==== TIER 2: CONTROLLERS ====
    color_t2 = "#C1FFC1"
    c_xacthuc = add_class(t2_id, "DieuKhienXacThuc", [
        "- user_dao: NguoiDung"
    ], [
        "+ authenticate()", "+ register()", "+ find_account_for_reset()", "+ reset_password()"
    ], color_t2, 100, 40, 220, 120)
    nodes['DieuKhienXacThuc'] = c_xacthuc

    c_nguoidung = add_class(t2_id, "DieuKhienNguoiDung", [
        "- user_dao: NguoiDung"
    ], [
        "+ list_users()", "+ save_user()", "+ delete_user()"
    ], color_t2, 100, 180, 220, 100)
    nodes['DieuKhienNguoiDung'] = c_nguoidung

    c_phong = add_class(t2_id, "DieuKhienPhong", [
        "- room_dao: PhongHoc"
    ], [
        "+ list_rooms()", "+ get_room()", "+ save_room()", 
        "+ delete_room()", "+ get_available_rooms()"
    ], color_t2, 450, 40, 220, 140)
    nodes['DieuKhienPhong'] = c_phong

    c_thietbi = add_class(t2_id, "DieuKhienThietBi", [
        "- equip_dao: ThietBi"
    ], [
        "+ list_equipment()", "+ save_equipment()", "+ delete_equipment()"
    ], color_t2, 450, 200, 220, 100)
    nodes['DieuKhienThietBi'] = c_thietbi

    c_lich = add_class(t2_id, "DieuKhienLich", [
        "- schedule_dao: LichPhong"
    ], [
        "+ list_schedule()", "+ save_schedule()", "+ delete_schedule()"
    ], color_t2, 700, 200, 200, 100)
    nodes['DieuKhienLich'] = c_lich

    c_datphong = add_class(t2_id, "DieuKhienDatPhong", [
        "- booking_dao: DatPhong"
    ], [
        "+ list_bookings()", "+ available_slots()", "+ create_booking()", 
        "+ update_status()", "+ update_booking()", "+ delete_booking()"
    ], color_t2, 920, 40, 200, 160)
    nodes['DieuKhienDatPhong'] = c_datphong

    c_baocao = add_class(t2_id, "DieuKhienBaoCao", [
        "- room_ctrl", "- booking_ctrl", "- user_ctrl", "- equip_ctrl"
    ], [
        "+ build_dashboard()", "+ room_usage_rows()", "+ room_stats_table()"
    ], color_t2, 920, 220, 200, 120)
    nodes['DieuKhienBaoCao'] = c_baocao

    c_phanhoi = add_class(t2_id, "DieuKhienPhanHoiPhong", [
        "- rating_dao", "- issue_dao"
    ], [
        "+ add_rating()", "+ get_ratings()", "+ average_stars()", 
        "+ report_issue()", "+ get_issues()"
    ], color_t2, 1150, 40, 220, 120)
    nodes['DieuKhienPhanHoiPhong'] = c_phanhoi

    # ==== TIER 1: UI / VIEW ====
    # Using generic UC UI classes since none are explicitly defined in the class diagram with attributes
    color_t1 = "#DCDCDC"
    ui_xacthuc = add_class(t1_id, "UI_DangNhap_DangKy (UC)", [], ["+ hien_thi_form()", "+ xu_ly_dang_nhap()", "+ xu_ly_dang_ky()"], color_t1, 100, 40, 220, 80)
    ui_nguoidung = add_class(t1_id, "UI_QuanLyNguoiDung (UC)", [], ["+ hien_thi_danh_sach()", "+ them_sua_xoa_user()"], color_t1, 100, 140, 220, 80)
    
    ui_phong = add_class(t1_id, "UI_QuanLyPhong (UC)", [], ["+ hien_thi_phong()", "+ them_sua_xoa_phong()"], color_t1, 450, 40, 220, 80)
    ui_thietbi = add_class(t1_id, "UI_QuanLyThietBi (UC)", [], ["+ hien_thi_thiet_bi()", "+ cap_nhat_thiet_bi()"], color_t1, 450, 140, 220, 80)
    
    ui_lich = add_class(t1_id, "UI_QuanLyLich (UC)", [], ["+ xem_lich_phong()", "+ cap_nhat_lich()"], color_t1, 700, 140, 200, 80)
    
    ui_datphong = add_class(t1_id, "UI_DatPhong (UC)", [], ["+ xem_phong_trong()", "+ tao_yeu_cau_dat()"], color_t1, 920, 40, 200, 80)
    ui_baocao = add_class(t1_id, "UI_BaoCaoThongKe (UC)", [], ["+ hien_thi_dashboard()", "+ xuat_bao_cao()"], color_t1, 920, 140, 200, 80)
    
    ui_phanhoi = add_class(t1_id, "UI_DanhGia_SuCo (UC)", [], ["+ gui_danh_gia()", "+ bao_cao_su_co()"], color_t1, 1150, 40, 220, 80)

    # ==== EDGES ====
    edge_dependency = "endArrow=classic;html=1;edgeStyle=orthogonalEdgeStyle;dashed=1;"
    edge_association = "endArrow=none;html=1;edgeStyle=orthogonalEdgeStyle;"
    edge_directed_assoc = "endArrow=classic;html=1;edgeStyle=orthogonalEdgeStyle;"
    edge_composition = "endArrow=none;html=1;edgeStyle=orthogonalEdgeStyle;startArrow=diamond;startFill=1;"

    # Connect UI (Tier 1) to Controllers (Tier 2) - Dependency
    add_edge(1, ui_xacthuc, c_xacthuc, edge_dependency)
    add_edge(1, ui_nguoidung, c_nguoidung, edge_dependency)
    add_edge(1, ui_phong, c_phong, edge_dependency)
    add_edge(1, ui_thietbi, c_thietbi, edge_dependency)
    add_edge(1, ui_lich, c_lich, edge_dependency)
    add_edge(1, ui_datphong, c_datphong, edge_dependency)
    add_edge(1, ui_baocao, c_baocao, edge_dependency)
    add_edge(1, ui_phanhoi, c_phanhoi, edge_dependency)

    # Connect Controllers (Tier 2) to Models (Tier 3) - Dependency
    add_edge(1, c_xacthuc, m_nguoidung, edge_dependency)
    add_edge(1, c_nguoidung, m_nguoidung, edge_dependency)
    add_edge(1, c_phong, m_phonghoc, edge_dependency)
    add_edge(1, c_thietbi, m_thietbi, edge_dependency)
    add_edge(1, c_lich, m_lichphong, edge_dependency)
    add_edge(1, c_datphong, m_datphong, edge_dependency)
    add_edge(1, c_phanhoi, m_danhgiaphong, edge_dependency)
    add_edge(1, c_phanhoi, m_sucophong, edge_dependency)

    # Cross dependencies for BaoCao and DatPhong
    add_edge(1, c_datphong, m_phonghoc, edge_dependency)
    add_edge(1, c_baocao, m_phonghoc, edge_dependency)

    # ==== MODEL RELATIONS (TIER 3) ====
    # Composition: PhongHoc has ThietBi and LichPhong (Black Diamond at PhongHoc)
    add_edge(t3_id, m_phonghoc, m_thietbi, edge_composition, "1  *")
    add_edge(t3_id, m_phonghoc, m_lichphong, edge_composition, "1  *")

    # Association: NguoiDung with DatPhong, DanhGiaPhong, SuCoPhong
    add_edge(t3_id, m_nguoidung, m_datphong, edge_directed_assoc, "1  *")
    add_edge(t3_id, m_nguoidung, m_danhgiaphong, edge_directed_assoc, "1  *")
    add_edge(t3_id, m_nguoidung, m_sucophong, edge_directed_assoc, "1  *")

    # Association: PhongHoc with DatPhong, DanhGiaPhong, SuCoPhong
    add_edge(t3_id, m_phonghoc, m_datphong, edge_directed_assoc, "1  *")
    add_edge(t3_id, m_phonghoc, m_danhgiaphong, edge_directed_assoc, "1  *")
    add_edge(t3_id, m_phonghoc, m_sucophong, edge_directed_assoc, "1  *")

    xml_str = ET.tostring(mxfile, encoding="unicode", xml_declaration=False)
    with open("../Docs/Design/Bieu do/MoHinh3Tier_ClassDiagram.drawio", "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(xml_str)

create_full_drawio()
