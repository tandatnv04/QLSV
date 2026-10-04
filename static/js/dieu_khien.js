/**
 * ĐIỀU KHIỂN GIAO DIỆN (UI CONTROLLER) - EDUPRO ENTERPRISE
 * 
 * HỖ TRỢ 2 CHẾ ĐỘ HOẠT ĐỘNG (DUAL MODE):
 * 1. Chế độ Backend Python (FastAPI): Khi chạy ở Localhost hoặc Hosting có Python, web gọi các API tại /api/...
 * 2. Chế độ GitHub Pages / Firebase Trực Tiếp: Khi deploy lên GitHub Pages (hoặc môi trường web tĩnh),
 *    hệ thống tự động chuyển sang đọc/ghi trực tiếp với Firebase Realtime Database theo đúng chuẩn dữ liệu
 *    tiếng Việt có dấu (người_dùng, môn_học, lịch_học, đăng_ký_học_phần, điểm_danh).
 */

const dieuKhien = {
  nguoiDungHienTai: null,
  phanKhuHienTai: 'dashboard',
  boLocVaiTroAdmin: 'all',
  phongToAnh: 1.0,
  gocXoayAnh: 0,
  khoaGiaoDien: 'SMS_THEME_MODE_V3',
  khoaLuuTruCucBo: 'EDUPRO_TIENG_VIET_DB_V4',
  khoaPhienCucBo: 'EDUPRO_PHIEN_DANG_NHAP_V4',
  cheDoHoatDong: 'tu_dong', // 'fastapi' | 'firebase'
  duLieuCucBo: null,

  // -------------------------------------------------------------
  // CẤU HÌNH & KẾT NỐI FIREBASE CLIENT
  // -------------------------------------------------------------
  get firebaseConfigured() {
    return typeof FIREBASE_CONFIG !== 'undefined' && FIREBASE_CONFIG.databaseURL && FIREBASE_CONFIG.databaseURL.startsWith('http');
  },

  get firebaseUrl() {
    if (!this.firebaseConfigured) return '';
    return FIREBASE_CONFIG.databaseURL.trim().replace(/\/$/, '');
  },

  async firebaseDoc(nhanh = '') {
    if (!this.firebaseConfigured) return null;
    try {
      const url = nhanh ? `${this.firebaseUrl}/${nhanh}.json` : `${this.firebaseUrl}/.json`;
      const res = await fetch(url);
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn('Lỗi đọc Firebase:', e);
    }
    return null;
  },

  async firebaseGhi(nhanh = '', duLieu = {}) {
    if (!this.firebaseConfigured) return false;
    try {
      const url = nhanh ? `${this.firebaseUrl}/${nhanh}.json` : `${this.firebaseUrl}/.json`;
      const res = await fetch(url, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(duLieu),
      });
      return res.ok;
    } catch (e) {
      console.warn('Lỗi ghi Firebase:', e);
      return false;
    }
  },

  async firebaseCapNhat(nhanh = '', duLieu = {}) {
    if (!this.firebaseConfigured) return false;
    try {
      const url = nhanh ? `${this.firebaseUrl}/${nhanh}.json` : `${this.firebaseUrl}/.json`;
      const res = await fetch(url, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(duLieu),
      });
      return res.ok;
    } catch (e) {
      console.warn('Lỗi cập nhật Firebase:', e);
      return false;
    }
  },

  // -------------------------------------------------------------
  // TỰ ĐỘNG PHÁT HIỆN CHẾ ĐỘ MÔI TRƯỜNG (FASTAPI HOẶC GITHUB PAGES)
  // -------------------------------------------------------------
  async xacDinhCheDo() {
    const isGithubPages = window.location.hostname.endsWith('github.io');
    if (isGithubPages) {
      this.cheDoHoatDong = 'firebase';
      console.log('[EduPro] Đang chạy trên GitHub Pages -> Tự động kích hoạt chế độ kết nối Firebase Trực Tiếp!');
      return;
    }

    try {
      const kiemTra = await fetch('/api/thong-ke/tong-quan', { credentials: 'same-origin' });
      if (kiemTra.status !== 404 && kiemTra.status !== 502) {
        this.cheDoHoatDong = 'fastapi';
        console.log('[EduPro] Kết nối thành công với Backend Python FastAPI!');
        return;
      }
    } catch (e) {}

    this.cheDoHoatDong = 'firebase';
    console.log('[EduPro] Không phát hiện FastAPI -> Chuyển sang chế độ kết nối Firebase Trực Tiếp!');
  },

  chuanHoaBanGhi(x) {
    if (!x || typeof x !== 'object') return x;
    const id = x.id || x.định_danh;
    if (id) {
      x.id = id;
      x.định_danh = id;
    }
    if (x.id_môn || x.định_danh_môn) {
      const monId = x.id_môn || x.định_danh_môn;
      x.id_môn = monId;
      x.định_danh_môn = monId;
    }
    if (x.id_giảng_viên || x.định_danh_giảng_viên) {
      const gvId = x.id_giảng_viên || x.định_danh_giảng_viên;
      x.id_giảng_viên = gvId;
      x.định_danh_giảng_viên = gvId;
    }
    if (x.id_sinh_viên || x.định_danh_sinh_viên) {
      const svId = x.id_sinh_viên || x.định_danh_sinh_viên;
      x.id_sinh_viên = svId;
      x.định_danh_sinh_viên = svId;
    }
    if (x.id_lịch_học || x.định_danh_lịch_học) {
      const lhId = x.id_lịch_học || x.định_danh_lịch_học;
      x.id_lịch_học = lhId;
      x.định_danh_lịch_học = lhId;
    }
    if (Array.isArray(x.danh_sách)) {
      x.danh_sách.forEach(sub => {
        if (sub && (sub.id_sinh_viên || sub.định_danh_sinh_viên)) {
          const sid = sub.id_sinh_viên || sub.định_danh_sinh_viên;
          sub.id_sinh_viên = sid;
          sub.định_danh_sinh_viên = sid;
        }
      });
    }
    return x;
  },

  chuanHoaDuLieu(db) {
    if (!db) return db;
    ['người_dùng', 'môn_học', 'lịch_học', 'đăng_ký_học_phần', 'điểm_danh'].forEach(bang => {
      (db[bang] || []).forEach(item => this.chuanHoaBanGhi(item));
    });
    return db;
  },

  // -------------------------------------------------------------
  // ĐỒNG BỘ DỮ LIỆU CỤC BỘ TRONG CHẾ ĐỘ FIREBASE
  // -------------------------------------------------------------
  async napDuLieuFirebase() {
    if (this.cheDoHoatDong !== 'firebase') return;

    // 1. Thử lấy từ Firebase
    const data = await this.firebaseDoc();
    if (data && data['người_dùng']) {
      this.duLieuCucBo = {
        người_dùng: Array.isArray(data['người_dùng']) ? data['người_dùng'] : Object.values(data['người_dùng'] || {}),
        môn_học: Array.isArray(data['môn_học']) ? data['môn_học'] : Object.values(data['môn_học'] || {}),
        lịch_học: Array.isArray(data['lịch_học']) ? data['lịch_học'] : Object.values(data['lịch_học'] || {}),
        đăng_ký_học_phần: Array.isArray(data['đăng_ký_học_phần']) ? data['đăng_ký_học_phần'] : Object.values(data['đăng_ký_học_phần'] || {}),
        điểm_danh: Array.isArray(data['điểm_danh']) ? data['điểm_danh'] : Object.values(data['điểm_danh'] || {}),
      };
      this.chuanHoaDuLieu(this.duLieuCucBo);
      localStorage.setItem(this.khoaLuuTruCucBo, JSON.stringify(this.duLieuCucBo));
      return;
    }

    // 2. Thử lấy từ LocalStorage
    const saved = localStorage.getItem(this.khoaLuuTruCucBo);
    if (saved) {
      try {
        this.duLieuCucBo = JSON.parse(saved);
        this.chuanHoaDuLieu(this.duLieuCucBo);
        return;
      } catch (e) {}
    }

    // 3. Nạp dữ liệu mẫu ban đầu nếu trống hoàn toàn
    try {
      const res = await fetch('du_lieu/du_lieu_mau.json');
      if (res.ok) {
        const seed = await res.json();
        this.duLieuCucBo = {
          người_dùng: Object.values(seed['người_dùng'] || {}),
          môn_học: Object.values(seed['môn_học'] || {}),
          lịch_học: Object.values(seed['lịch_học'] || {}),
          đăng_ký_học_phần: Object.values(seed['đăng_ký_học_phần'] || {}),
          điểm_danh: Object.values(seed['điểm_danh'] || {}),
        };
        this.chuanHoaDuLieu(this.duLieuCucBo);
        localStorage.setItem(this.khoaLuuTruCucBo, JSON.stringify(this.duLieuCucBo));
        // Đồng bộ lên Firebase luôn
        this.firebaseGhi('', seed);
      }
    } catch (e) {}
  },

  luuDuLieuFirebase() {
    if (!this.duLieuCucBo) return;
    this.chuanHoaDuLieu(this.duLieuCucBo);
    localStorage.setItem(this.khoaLuuTruCucBo, JSON.stringify(this.duLieuCucBo));
    
    // Đồng bộ lên Firebase dạng object theo id
    if (this.firebaseConfigured) {
      const dongBo = {
        người_dùng: {},
        môn_học: {},
        lịch_học: {},
        đăng_ký_học_phần: {},
        điểm_danh: {},
      };
      (this.duLieuCucBo.người_dùng || []).forEach(x => { const id = x.id || x.định_danh; dongBo.người_dùng[id] = x; });
      (this.duLieuCucBo.môn_học || []).forEach(x => { const id = x.id || x.định_danh; dongBo.môn_học[id] = x; });
      (this.duLieuCucBo.lịch_học || []).forEach(x => { const id = x.id || x.định_danh; dongBo.lịch_học[id] = x; });
      (this.duLieuCucBo.đăng_ký_học_phần || []).forEach(x => { const id = x.id || x.định_danh; dongBo.đăng_ký_học_phần[id] = x; });
      (this.duLieuCucBo.điểm_danh || []).forEach(x => { const id = x.id || x.định_danh; dongBo.điểm_danh[id] = x; });
      this.firebaseGhi('', dongBo);
    }
  },

  // -------------------------------------------------------------
  // BỘ GỌI API THỐNG NHẤT
  // -------------------------------------------------------------
  async goiApi(duongDan, phuongThuc = 'GET', duLieu = null) {
    if (this.cheDoHoatDong === 'fastapi') {
      const options = {
        method: phuongThuc,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
      };
      if (duLieu && (phuongThuc === 'POST' || phuongThuc === 'PUT' || phuongThuc === 'PATCH')) {
        options.body = JSON.stringify(duLieu);
      }

      try {
        const res = await fetch(duongDan, options);
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data?.thông_báo || data?.detail || 'Có lỗi xảy ra!');
        }
        return data;
      } catch (err) {
        this.toast('error', err.message);
        throw err;
      }
    }

    // CHẾ ĐỘ FIREBASE TRỰC TIẾP (CHO GITHUB PAGES)
    return this.xuLyFirebaseClient(duongDan, phuongThuc, duLieu);
  },

  // Giả lập router bằng Firebase client-side khi chạy trên GitHub Pages
  async xuLyFirebaseClient(duongDan, phuongThuc, duLieu) {
    if (!this.duLieuCucBo) await this.napDuLieuFirebase();
    const db = this.duLieuCucBo;

    // 1. Xác thực
    if (duongDan === '/api/xac-thuc/dang-nhap') {
      const user = db.người_dùng.find(u => u.tên_đăng_nhập === duLieu.tên_đăng_nhập && u.mật_khẩu === duLieu.mật_khẩu);
      if (!user) {
        this.toast('error', 'Tên đăng nhập hoặc mật khẩu không chính xác!');
        throw new Error('Sai tài khoản');
      }
      if (user.trạng_thái === 'Đã khóa') {
        this.toast('error', 'Tài khoản này đã bị khóa!');
        throw new Error('Tài khoản bị khóa');
      }
      localStorage.setItem(this.khoaPhienCucBo, JSON.stringify(user));
      return { thành_công: true, thông_báo: `Chào mừng ${user.họ_tên}!`, người_dùng: user };
    }

    if (duongDan === '/api/xac-thuc/dang-xuat') {
      localStorage.removeItem(this.khoaPhienCucBo);
      return { thành_công: true, thông_báo: 'Đã đăng xuất' };
    }

    if (duongDan === '/api/xac-thuc/quen-mat-khau') {
      const ident = duLieu.thông_tin_tài_khoản.toLowerCase();
      const user = db.người_dùng.find(u => 
        (u.tên_đăng_nhập && u.tên_đăng_nhập.toLowerCase() === ident) ||
        (u.email && u.email.toLowerCase() === ident) ||
        (u.mã_số && u.mã_số.toLowerCase() === ident)
      );
      if (!user) {
        this.toast('error', 'Không tìm thấy tài khoản tương ứng!');
        throw new Error('Không tìm thấy tài khoản');
      }
      user.mật_khẩu = duLieu.mật_khẩu_mới;
      this.luuDuLieuFirebase();
      return { thành_công: true, thông_báo: `Đã đặt lại mật khẩu cho ${user.họ_tên} thành công!` };
    }

    // 2. Thống kê
    if (duongDan === '/api/thong-ke/tong-quan') {
      const soGV = db.người_dùng.filter(u => u.vai_trò === 'Giảng viên').length;
      const soSV = db.người_dùng.filter(u => u.vai_trò === 'Sinh viên').length;
      const soMon = db.môn_học.length;
      const soLich = db.lịch_học.length;

      const phanBo = {};
      db.môn_học.forEach(m => {
        const k = m.khoa || 'Chung';
        phanBo[k] = (phanBo[k] || 0) + 1;
      });
      const danhSachPhanBo = Object.entries(phanBo).map(([khoa, count]) => ({
        khoa,
        số_lượng: count,
        tỷ_lệ: Math.round((count / (soMon || 1)) * 100),
      }));

      return {
        thành_công: true,
        số_giảng_viên: soGV,
        số_sinh_viên: soSV,
        số_môn_học: soMon,
        số_lịch_dạy: soLich,
        phân_bố_khoa: danhSachPhanBo,
      };
    }

    // 3. Hồ sơ
    if (duongDan === '/api/ho-so') {
      if (phuongThuc === 'GET') {
        return { thành_công: true, hồ_sơ: this.nguoiDungHienTai };
      }
      if (phuongThuc === 'PUT') {
        Object.assign(this.nguoiDungHienTai, duLieu);
        const idx = db.người_dùng.findIndex(u => u.định_danh === this.nguoiDungHienTai.định_danh);
        if (idx !== -1) db.người_dùng[idx] = { ...this.nguoiDungHienTai };
        this.luuDuLieuFirebase();
        localStorage.setItem(this.khoaPhienCucBo, JSON.stringify(this.nguoiDungHienTai));
        return { thành_công: true, thông_báo: 'Đã lưu thông tin hồ sơ!', hồ_sơ: this.nguoiDungHienTai };
      }
    }

    if (duongDan === '/api/ho-so/anh-dai-dien') {
      if (phuongThuc === 'POST') {
        this.nguoiDungHienTai.ảnh_đại_diện = duLieu.ảnh_đại_diện;
      } else {
        delete this.nguoiDungHienTai.ảnh_đại_diện;
      }
      const idx = db.người_dùng.findIndex(u => u.định_danh === this.nguoiDungHienTai.định_danh);
      if (idx !== -1) db.người_dùng[idx] = { ...this.nguoiDungHienTai };
      this.luuDuLieuFirebase();
      localStorage.setItem(this.khoaPhienCucBo, JSON.stringify(this.nguoiDungHienTai));
      return { thành_công: true, thông_báo: 'Đã cập nhật ảnh đại diện!', hồ_sơ: this.nguoiDungHienTai };
    }

    // 4. Môn học
    if (duongDan === '/api/mon-hoc') {
      if (phuongThuc === 'GET') {
        const list = db.môn_học.map(m => ({
          ...m,
          số_tín_chỉ: m.số_tín_chỉ || 3,
          đơn_giá_tín_chỉ: m.đơn_giá_tín_chỉ || 450000,
          tổng_học_phí: (m.số_tín_chỉ || 3) * (m.đơn_giá_tín_chỉ || 450000),
        }));
        return { thành_công: true, danh_sách: list };
      }
      if (phuongThuc === 'POST') {
        const newMon = {
          định_danh: 'mh_' + Date.now(),
          ...duLieu,
          ngày_mở_nhập_điểm: '2026-09-15',
          ngày_chốt_điểm: '2026-10-20',
          khóa_nhập_điểm: false,
        };
        db.môn_học.push(newMon);
        this.luuDuLieuFirebase();
        return { thành_công: true, thông_báo: `Đã thêm môn ${newMon.tên_môn}!`, môn_học: newMon };
      }
    }

    if (duongDan.startsWith('/api/mon-hoc/') && duongDan.endsWith('/han-nhap-diem')) {
      const mhId = duongDan.split('/')[3];
      const mon = db.môn_học.find(m => m.định_danh === mhId);
      if (mon) {
        Object.assign(mon, duLieu);
        this.luuDuLieuFirebase();
        return { thành_công: true, thông_báo: `Đã cập nhật hạn nhập điểm cho môn ${mon.mã_môn}!`, môn_học: mon };
      }
    }

    if (duongDan.startsWith('/api/mon-hoc/') && phuongThuc === 'DELETE') {
      const mhId = duongDan.split('/')[3];
      db.môn_học = db.môn_học.filter(m => m.định_danh !== mhId);
      db.lịch_học = db.lịch_học.filter(l => l.định_danh_môn !== mhId);
      db.đăng_ký_học_phần = db.đăng_ký_học_phần.filter(d => d.định_danh_môn !== mhId);
      this.luuDuLieuFirebase();
      return { thành_công: true, thông_báo: 'Đã xóa môn học thành công!' };
    }

    // 5. Người dùng
    if (duongDan.startsWith('/api/nguoi-dung/sinh-vien')) {
      const list = db.người_dùng.filter(u => u.vai_trò === 'Sinh viên');
      return { thành_công: true, danh_sách: list };
    }
    if (duongDan === '/api/nguoi-dung/giang-vien') {
      const list = db.người_dùng.filter(u => u.vai_trò === 'Giảng viên');
      return { thành_công: true, danh_sách: list };
    }
    if (duongDan.startsWith('/api/nguoi-dung') && phuongThuc === 'GET') {
      return { thành_công: true, danh_sách: db.người_dùng };
    }
    if (duongDan === '/api/nguoi-dung' && phuongThuc === 'POST') {
      const newUser = {
        định_danh: 'nd_' + Date.now(),
        ...duLieu,
        trạng_thái: 'Hoạt động',
      };
      db.người_dùng.push(newUser);
      this.luuDuLieuFirebase();
      return { thành_công: true, thông_báo: `Đã tạo tài khoản cho ${newUser.họ_tên}!`, người_dùng: newUser };
    }
    if (duongDan.startsWith('/api/nguoi-dung/') && duongDan.endsWith('/khoa')) {
      const uId = duongDan.split('/')[3];
      const user = db.người_dùng.find(u => u.định_danh === uId);
      if (user) {
        user.trạng_thái = user.trạng_thái === 'Đã khóa' ? 'Hoạt động' : 'Đã khóa';
        this.luuDuLieuFirebase();
        return { thành_công: true, thông_báo: `Đã ${user.trạng_thái === 'Đã khóa' ? 'tạm khóa' : 'mở khóa'} tài khoản!`, người_dùng: user };
      }
    }
    if (duongDan.startsWith('/api/nguoi-dung/') && phuongThuc === 'PUT') {
      const uId = duongDan.split('/')[3];
      const user = db.người_dùng.find(u => u.định_danh === uId);
      if (user) {
        Object.assign(user, duLieu);
        if (duLieu.mật_khẩu_mới) user.mật_khẩu = duLieu.mật_khẩu_mới;
        this.luuDuLieuFirebase();
        return { thành_công: true, thông_báo: `Đã cập nhật thông tin cho ${user.họ_tên}!`, người_dùng: user };
      }
    }
    if (duongDan.startsWith('/api/nguoi-dung/') && phuongThuc === 'DELETE') {
      const uId = duongDan.split('/')[3];
      db.người_dùng = db.người_dùng.filter(u => u.định_danh !== uId);
      this.luuDuLieuFirebase();
      return { thành_công: true, thông_báo: 'Đã xóa tài khoản khỏi hệ thống!' };
    }

    // 6. Thời khóa biểu
    if (duongDan.startsWith('/api/lich-hoc')) {
      if (phuongThuc === 'GET') {
        const user = this.nguoiDungHienTai;
        let list = [...db.lịch_học];
        let chuaDangKy = false;

        if (user.vai_trò === 'Giảng viên') {
          list = list.filter(l => l.định_danh_giảng_viên === user.định_danh || (l.tên_giảng_viên && l.tên_giảng_viên.includes(user.họ_tên)));
        } else if (user.vai_trò === 'Sinh viên') {
          const monIds = db.đăng_ký_học_phần.filter(d => d.định_danh_sinh_viên === user.định_danh).map(d => d.định_danh_môn);
          chuaDangKy = monIds.length === 0;
          list = list.filter(l => monIds.includes(l.định_danh_môn));
        }

        const urlObj = new URL('http://dummy' + duongDan);
        const tuan = urlObj.searchParams.get('tuan');
        const thu = urlObj.searchParams.get('thu');
        if (tuan) list = list.filter(l => l.tuần == tuan);
        if (thu) list = list.filter(l => l.thứ === thu);

        return { thành_công: true, danh_sách: list, chưa_đăng_ký_môn: chuaDangKy };
      }
      if (phuongThuc === 'POST') {
        const mon = db.môn_học.find(m => m.định_danh === duLieu.định_danh_môn);
        const gv = db.người_dùng.find(u => u.định_danh === duLieu.định_danh_giảng_viên);
        const newLich = {
          định_danh: 'lh_' + Date.now(),
          ...duLieu,
          mã_môn: mon?.mã_môn || '',
          tên_môn: mon?.tên_môn || '',
          tên_giảng_viên: gv?.họ_tên || '',
        };
        db.lịch_học.push(newLich);
        this.luuDuLieuFirebase();
        return { thành_công: true, thông_báo: 'Đã xếp lịch giảng dạy thành công!', lịch_học: newLich };
      }
    }

    // 7. Điểm danh
    if (duongDan.startsWith('/api/diem-danh')) {
      if (phuongThuc === 'GET') {
        const urlObj = new URL('http://dummy' + duongDan);
        const schedId = urlObj.searchParams.get('dinh_danh_lich');
        const ngay = urlObj.searchParams.get('ngay');
        const sched = db.lịch_học.find(l => l.định_danh === schedId);

        // Lấy danh sách SV đã đăng ký môn này
        const svIds = db.đăng_ký_học_phần.filter(d => d.định_danh_môn === sched?.định_danh_môn).map(d => d.định_danh_sinh_viên);
        const svList = db.người_dùng.filter(u => svIds.includes(u.định_danh) || u.vai_trò === 'Sinh viên');

        const buoi = db.điểm_danh.find(d => d.định_danh_lịch_học === schedId && d.ngày === ngay);
        const daGhi = {};
        (buoi?.danh_sách || []).forEach(bg => daGhi[bg.định_danh_sinh_viên] = bg);

        const list = svList.map(s => ({
          định_danh: s.định_danh,
          mã_số: s.mã_số,
          họ_tên: s.họ_tên,
          ảnh_đại_diện: s.ảnh_đại_diện,
          trạng_thái: daGhi[s.định_danh]?.trạng_thái || 'Có mặt',
          ghi_chú: daGhi[s.định_danh]?.ghi_chú || '',
        }));

        return { thành_công: true, danh_sách: list, đã_điểm_danh: !!buoi };
      }
      if (phuongThuc === 'POST') {
        const idx = db.điểm_danh.findIndex(d => d.định_danh_lịch_học === duLieu.định_danh_lịch_học && d.ngày === duLieu.ngày);
        if (idx !== -1) {
          db.điểm_danh[idx] = { định_danh: db.điểm_danh[idx].định_danh, ...duLieu };
        } else {
          db.điểm_danh.push({ định_danh: 'dd_' + Date.now(), ...duLieu });
        }
        this.luuDuLieuFirebase();
        return { thành_công: true, thông_báo: `Đã lưu kết quả điểm danh ngày ${duLieu.ngày} thành công!` };
      }
    }

    // 8. Điểm số
    if (duongDan.startsWith('/api/diem-so/so-diem/')) {
      const parts = duongDan.split('/');
      const mhId = parts[4];

      if (phuongThuc === 'GET') {
        const mon = db.môn_học.find(m => m.định_danh === mhId);
        const svList = db.người_dùng.filter(u => u.vai_trò === 'Sinh viên');

        const list = svList.map(s => {
          const dk = db.đăng_ký_học_phần.find(d => d.định_danh_môn === mhId && d.định_danh_sinh_viên === s.định_danh);
          const mid = dk?.điểm_giữa_kỳ ?? 8.0;
          const fin = dk?.điểm_cuối_kỳ ?? 8.5;
          const total = +(mid * 0.4 + fin * 0.6).toFixed(1);
          return {
            định_danh_sinh_viên: s.định_danh,
            mã_số: s.mã_số,
            họ_tên: s.họ_tên,
            điểm_giữa_kỳ: mid,
            điểm_cuối_kỳ: fin,
            điểm_tổng_kết: total,
            điểm_chữ: this.tinhDiemChu(total),
            điểm_hệ_4: this.tinhHe4(total),
            nhận_xét: dk?.nhận_xét || '',
          };
        });

        return {
          thành_công: true,
          môn_học: mon,
          cổng_điểm: {
            ngày_mở_nhập_điểm: mon?.ngày_mở_nhập_điểm || '2026-09-15',
            ngày_chốt_điểm: mon?.ngày_chốt_điểm || '2026-10-20',
            đã_khóa: !!mon?.khóa_nhập_điểm,
            được_phép_sửa: !mon?.khóa_nhập_điểm || this.nguoiDungHienTai?.vai_trò === 'Quản trị viên',
          },
          danh_sách: list,
        };
      }

      if (phuongThuc === 'PUT' && parts[5] === 'sinh-vien') {
        const svId = parts[6];
        let dk = db.đăng_ký_học_phần.find(d => d.định_danh_môn === mhId && d.định_danh_sinh_viên === svId);
        if (dk) {
          dk.điểm_giữa_kỳ = duLieu.điểm_giữa_kỳ;
          dk.điểm_cuối_kỳ = duLieu.điểm_cuối_kỳ;
          dk.nhận_xét = duLieu.nhận_xét;
        } else {
          dk = {
            định_danh: 'dk_' + Date.now(),
            định_danh_sinh_viên: svId,
            định_danh_môn: mhId,
            điểm_giữa_kỳ: duLieu.điểm_giữa_kỳ,
            điểm_cuối_kỳ: duLieu.điểm_cuối_kỳ,
            điểm_chuyên_cần: 10,
            nhận_xét: duLieu.nhận_xét,
            đã_đóng_học_phí: true,
          };
          db.đăng_ký_học_phần.push(dk);
        }
        this.luuDuLieuFirebase();
        return { thành_công: true, thông_báo: 'Đã lưu điểm cho sinh viên thành công!' };
      }
    }

    if (duongDan === '/api/diem-so/tinh-nhanh') {
      const mid = duLieu.điểm_giữa_kỳ || 0;
      const fin = duLieu.điểm_cuối_kỳ || 0;
      const total = +(mid * 0.4 + fin * 0.6).toFixed(1);
      return {
        điểm_tổng_kết: total,
        điểm_chữ: this.tinhDiemChu(total),
        điểm_hệ_4: this.tinhHe4(total),
      };
    }

    if (duongDan === '/api/diem-so/bang-diem-cua-toi' || duongDan.startsWith('/api/diem-so/bang-diem-sinh-vien/')) {
      const svId = duongDan.includes('bang-diem-sinh-vien') ? duongDan.split('/')[4] : this.nguoiDungHienTai.định_danh;
      const sv = db.người_dùng.find(u => u.định_danh === svId);
      const myDk = db.đăng_ký_học_phần.filter(d => d.định_danh_sinh_viên === svId);

      let tongTC = 0, tongDiem10 = 0, tongDiem4 = 0, tongHocPhi = 0, daDongHP = 0;
      const list = myDk.map(d => {
        const mon = db.môn_học.find(m => m.định_danh === d.định_danh_môn);
        const tc = mon?.số_tín_chỉ || 3;
        const gia = mon?.đơn_giá_tín_chỉ || 450000;
        const total = +(d.điểm_giữa_kỳ * 0.4 + d.điểm_cuối_kỳ * 0.6).toFixed(1);
        const he4 = this.tinhHe4(total);
        const chu = this.tinhDiemChu(total);

        tongTC += tc;
        tongDiem10 += total * tc;
        tongDiem4 += he4 * tc;
        tongHocPhi += tc * gia;
        if (d.đã_đóng_học_phí) daDongHP += tc * gia;

        return {
          định_danh: d.định_danh,
          mã_môn: mon?.mã_môn || '',
          tên_môn: mon?.tên_môn || 'Môn học',
          khoa: mon?.khoa || '',
          học_kỳ: mon?.học_kỳ || '',
          số_tín_chỉ: tc,
          điểm_giữa_kỳ: d.điểm_giữa_kỳ,
          điểm_cuối_kỳ: d.điểm_cuối_kỳ,
          điểm_tổng_kết: total,
          điểm_chữ: chu,
          điểm_hệ_4: he4,
          mức: total >= 8.0 ? 'tốt' : (total >= 6.5 ? 'khá' : 'yếu'),
          nhận_xét: d.nhận_xét,
          đã_đóng_học_phí: d.đã_đóng_học_phí,
        };
      });

      const gpa10 = tongTC > 0 ? +(tongDiem10 / tongTC).toFixed(2) : 0;
      const gpa4 = tongTC > 0 ? +(tongDiem4 / tongTC).toFixed(2) : 0;

      return {
        thành_công: true,
        sinh_viên: sv,
        kết_quả_học_tập: list,
        tổng_kết: {
          tổng_tín_chỉ: tongTC,
          gpa_hệ_10: gpa10,
          gpa_hệ_4: gpa4,
          xếp_loại: gpa10 >= 8.0 ? 'Giỏi' : (gpa10 >= 6.5 ? 'Khá' : 'Trung bình'),
          mức: gpa10 >= 8.0 ? 'tốt' : (gpa10 >= 6.5 ? 'khá' : 'yếu'),
          học_phí_đã_đóng: daDongHP,
          tổng_học_phí: tongHocPhi,
          đã_hoàn_thành_học_phí: daDongHP >= tongHocPhi && tongHocPhi > 0,
        }
      };
    }

    // 9. Đăng ký học phần & học phí
    if (duongDan === '/api/hoc-phan/danh-sach-mo') {
      const svId = this.nguoiDungHienTai.định_danh;
      const daDkIds = db.đăng_ký_học_phần.filter(d => d.định_danh_sinh_viên === svId).map(d => d.định_danh_môn);
      const list = db.môn_học.map(m => ({
        ...m,
        đã_đăng_ký: daDkIds.includes(m.định_danh),
      }));
      return { thành_công: true, danh_sách: list };
    }

    if (duongDan.startsWith('/api/hoc-phan/dang-ky/')) {
      const mhId = duongDan.split('/')[4];
      const svId = this.nguoiDungHienTai.định_danh;
      const exists = db.đăng_ký_học_phần.some(d => d.định_danh_sinh_viên === svId && d.định_danh_môn === mhId);
      if (exists) {
        this.toast('warning', 'Bạn đã đăng ký học phần này rồi!');
        return { thành_công: false };
      }
      db.đăng_ký_học_phần.push({
        định_danh: 'dk_' + Date.now(),
        định_danh_sinh_viên: svId,
        định_danh_môn: mhId,
        điểm_giữa_kỳ: 0,
        điểm_cuối_kỳ: 0,
        điểm_chuyên_cần: 10,
        nhận_xét: 'Mới đăng ký học phần',
        đã_đóng_học_phí: false,
      });
      this.luuDuLieuFirebase();
      return { thành_công: true, thông_báo: 'Đăng ký học phần thành công!' };
    }

    if (duongDan.startsWith('/api/hoc-phan/huy-dang-ky/')) {
      const mhId = duongDan.split('/')[4];
      const svId = this.nguoiDungHienTai.định_danh;
      db.đăng_ký_học_phần = db.đăng_ký_học_phần.filter(d => !(d.định_danh_sinh_viên === svId && d.định_danh_môn === mhId));
      this.luuDuLieuFirebase();
      return { thành_công: true, thông_báo: 'Đã hủy đăng ký học phần.' };
    }

    if (duongDan === '/api/hoc-phan/hoc-phi') {
      const svId = this.nguoiDungHienTai.định_danh;
      const myDk = db.đăng_ký_học_phần.filter(d => d.định_danh_sinh_viên === svId);
      let tongTC = 0, tongTien = 0, allPaid = myDk.length > 0;

      const list = myDk.map(d => {
        const mon = db.môn_học.find(m => m.định_danh === d.định_danh_môn);
        const tc = mon?.số_tín_chỉ || 3;
        const gia = mon?.đơn_giá_tín_chỉ || 450000;
        const tt = tc * gia;
        tongTC += tc;
        tongTien += tt;
        if (!d.đã_đóng_học_phí) allPaid = false;

        return {
          mã_môn: mon?.mã_môn || '-',
          tên_môn: mon?.tên_môn || 'Môn học',
          số_tín_chỉ: tc,
          đơn_giá_tín_chỉ: gia,
          thành_tiền: tt,
          đã_đóng_học_phí: d.đã_đóng_học_phí,
        };
      });

      return {
        thành_công: true,
        danh_sách: list,
        tổng_tín_chỉ: tongTC,
        tổng_tiền: tongTien,
        tất_cả_đã_đóng: allPaid,
      };
    }

    if (duongDan === '/api/hoc-phan/hoc-phi/thanh-toan') {
      const svId = this.nguoiDungHienTai.định_danh;
      db.đăng_ký_học_phần.filter(d => d.định_danh_sinh_viên === svId).forEach(d => d.đã_đóng_học_phí = true);
      this.luuDuLieuFirebase();
      return { thành_công: true, thông_báo: 'Thanh toán học phí trực tuyến thành công!' };
    }

    if (duongDan.startsWith('/api/ho-so/the-thong-tin/')) {
      const uId = duongDan.split('/')[4];
      const user = db.người_dùng.find(u => u.định_danh === uId) || {};
      return { thành_công: true, thẻ: user };
    }

    return { thành_công: true };
  },

  tinhDiemChu(score) {
    if (score >= 8.5) return 'A';
    if (score >= 8.0) return 'B+';
    if (score >= 7.0) return 'B';
    if (score >= 6.5) return 'C+';
    if (score >= 5.5) return 'C';
    if (score >= 5.0) return 'D+';
    if (score >= 4.0) return 'D';
    return 'F';
  },

  tinhHe4(score) {
    if (score >= 8.5) return 4.0;
    if (score >= 8.0) return 3.5;
    if (score >= 7.0) return 3.0;
    if (score >= 6.5) return 2.5;
    if (score >= 5.5) return 2.0;
    if (score >= 5.0) return 1.5;
    if (score >= 4.0) return 1.0;
    return 0.0;
  },

  // -------------------------------------------------------------
  // KHỞI ĐỘNG ỨNG DỤNG
  // -------------------------------------------------------------
  async init() {
    this.initTheme();
    this.bindEvents();
    await this.xacDinhCheDo();

    if (this.cheDoHoatDong === 'firebase') {
      await this.napDuLieuFirebase();
      const savedUser = localStorage.getItem(this.khoaPhienCucBo);
      if (savedUser) {
        try {
          this.nguoiDungHienTai = JSON.parse(savedUser);
          this.renderAppForUser(this.nguoiDungHienTai);
          return;
        } catch (e) {}
      }
      this.showLogin();
      return;
    }

    // Chế độ FastAPI
    try {
      const res = await fetch('/api/xac-thuc/nguoi-dung-hien-tai', { credentials: 'same-origin' });
      if (res.ok) {
        const ketQua = await res.json();
        if (ketQua?.thành_công && ketQua?.người_dùng) {
          this.nguoiDungHienTai = ketQua.người_dùng;
          this.renderAppForUser(this.nguoiDungHienTai);
          return;
        }
      }
    } catch (e) {}
    this.showLogin();
  },

  initTheme() {
    const savedTheme = localStorage.getItem(this.khoaGiaoDien) || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
      themeIcon.className = savedTheme === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
    }
  },

  toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', nextTheme);
    localStorage.setItem(this.khoaGiaoDien, nextTheme);
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
      themeIcon.className = nextTheme === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
    }
    this.toast('success', `Đã chuyển sang giao diện ${nextTheme === 'dark' ? 'Tối' : 'Sáng'}`);
  },

  bindEvents() {
    const menuBtn = document.getElementById('sidebar-toggle-btn');
    if (menuBtn) {
      menuBtn.onclick = (e) => {
        if (e) e.preventDefault();
        this.toggleSidebar();
      };
    }
  },

  toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    const overlay = document.getElementById('sidebar-overlay');
    if (!sidebar) return;

    if (window.innerWidth <= 1024) {
      const isOpen = sidebar.classList.toggle('open');
      if (overlay) {
        if (isOpen) overlay.classList.add('show');
        else overlay.classList.remove('show');
      }
    } else {
      sidebar.classList.toggle('collapsed');
      if (mainContent) {
        mainContent.classList.toggle('expanded');
      }
    }
  },

  toast(type, message) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toastEl = document.createElement('div');
    toastEl.className = `toast ${type}`;
    
    let iconClass = 'fa-circle-check';
    if (type === 'error') iconClass = 'fa-circle-xmark';
    if (type === 'warning') iconClass = 'fa-triangle-exclamation';
    if (type === 'info') iconClass = 'fa-circle-info';

    toastEl.innerHTML = `
      <i class="fa-solid ${iconClass}" style="font-size:16px;"></i>
      <div style="flex:1;">${message}</div>
      <button onclick="this.parentElement.remove()" style="background:none;border:none;color:var(--text-muted);cursor:pointer;">&times;</button>
    `;

    container.appendChild(toastEl);
    setTimeout(() => {
      if (toastEl.parentElement) {
        toastEl.style.opacity = '0';
        toastEl.style.transform = 'translateX(40px)';
        setTimeout(() => toastEl.remove(), 250);
      }
    }, 3500);
  },

  // -------------------------------------------------------------
  // XÁC THỰC: ĐĂNG NHẬP / ĐĂNG XUẤT / QUÊN MẬT KHẨU
  // -------------------------------------------------------------
  async handleLogin(event) {
    event.preventDefault();
    const tenDangNhap = document.getElementById('login-username').value.trim();
    const matKhau = document.getElementById('login-password').value.trim();

    try {
      const ketQua = await this.goiApi('/api/xac-thuc/dang-nhap', 'POST', {
        tên_đăng_nhập: tenDangNhap,
        mật_khẩu: matKhau,
      });

      this.nguoiDungHienTai = ketQua.người_dùng;
      this.toast('success', ketQua.thông_báo || `Chào mừng ${this.nguoiDungHienTai.họ_tên}!`);
      this.renderAppForUser(this.nguoiDungHienTai);
    } catch (e) {}
  },

  async quickLogin(vaiTro) {
    let tenDangNhap = 'admin';
    if (vaiTro === 'teacher' || vaiTro === 'Giảng viên') tenDangNhap = 'teacher1';
    if (vaiTro === 'student' || vaiTro === 'Sinh viên') tenDangNhap = 'student1';

    try {
      const ketQua = await this.goiApi('/api/xac-thuc/dang-nhap', 'POST', {
        tên_đăng_nhập: tenDangNhap,
        mật_khẩu: '123',
      });
      this.nguoiDungHienTai = ketQua.người_dùng;
      this.toast('success', ketQua.thông_báo);
      this.renderAppForUser(this.nguoiDungHienTai);
    } catch (e) {}
  },

  async logout() {
    try {
      await this.goiApi('/api/xac-thuc/dang-xuat', 'POST');
    } catch (e) {}
    this.nguoiDungHienTai = null;
    this.toast('info', 'Bạn đã đăng xuất khỏi hệ thống');
    this.showLogin();
  },

  openForgotPasswordModal() {
    const ident = document.getElementById('forgot-identifier');
    const newPass = document.getElementById('forgot-new-password');
    const confirmPass = document.getElementById('forgot-confirm-password');
    if (ident) ident.value = '';
    if (newPass) newPass.value = '';
    if (confirmPass) confirmPass.value = '';
    this.openModal('modal-forgot-password');
  },

  async handleForgotPassword(event) {
    event.preventDefault();
    const identifier = (document.getElementById('forgot-identifier')?.value || '').trim();
    const newPassword = (document.getElementById('forgot-new-password')?.value || '').trim();
    const confirmPassword = (document.getElementById('forgot-confirm-password')?.value || '').trim();

    try {
      const ketQua = await this.goiApi('/api/xac-thuc/quen-mat-khau', 'POST', {
        thông_tin_tài_khoản: identifier,
        mật_khẩu_mới: newPassword,
        xác_nhận_mật_khẩu: confirmPassword,
      });
      this.closeModal('modal-forgot-password');
      this.toast('success', ketQua.thông_báo);
    } catch (e) {}
  },

  showLogin() {
    document.getElementById('auth-section').style.display = 'flex';
    document.getElementById('app-layout').style.display = 'none';
  },

  renderAppForUser(user) {
    document.getElementById('auth-section').style.display = 'none';
    document.getElementById('app-layout').style.display = 'flex';

    const avatar = document.getElementById('user-avatar-text');
    const nameEl = document.getElementById('user-display-name');
    const roleBadge = document.getElementById('user-role-badge');
    
    if (avatar) {
      if (user.ảnh_đại_diện) {
        avatar.innerHTML = `<img src="${user.ảnh_đại_diện}" alt="${user.họ_tên}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">`;
      } else {
        const initials = user.họ_tên ? user.họ_tên.split(' ').pop().charAt(0).toUpperCase() : 'U';
        avatar.innerText = initials;
      }
    }
    if (nameEl) nameEl.innerText = user.họ_tên || 'Người dùng';
    if (roleBadge) {
      roleBadge.innerText = user.vai_trò || 'Người dùng';
      roleBadge.className = `badge-role badge-${this.chuanHoaClassVaiTro(user.vai_trò)}`;
    }

    this.renderNavMenu(user.vai_trò);

    if (user.vai_trò === 'Quản trị viên') {
      this.switchSection('dashboard');
    } else {
      this.switchSection('schedule');
    }
  },

  chuanHoaClassVaiTro(vaiTro) {
    if (vaiTro === 'Quản trị viên') return 'admin';
    if (vaiTro === 'Giảng viên') return 'teacher';
    if (vaiTro === 'Sinh viên') return 'student';
    return 'student';
  },

  chuanHoaMaVaiTro(vaiTro) {
    if (vaiTro === 'admin') return 'Quản trị viên';
    if (vaiTro === 'teacher') return 'Giảng viên';
    if (vaiTro === 'student') return 'Sinh viên';
    return vaiTro;
  },

  renderNavMenu(vaiTro) {
    const menuEl = document.getElementById('nav-menu');
    let html = '';

    if (vaiTro === 'Quản trị viên') {
      html += `
        <div class="menu-category">Quản Trị Hệ Thống</div>
        <li class="nav-link active" onclick="app.switchSection('dashboard')">
          <i class="fa-solid fa-chart-pie"></i>
          <span>Bảng Điều Khiển</span>
        </li>
        <li class="nav-link" onclick="app.switchSection('admin-users')">
          <i class="fa-solid fa-user-shield"></i>
          <span>Phân Quyền & Tài Khoản</span>
        </li>
        <li class="nav-link" onclick="app.switchSection('admin-courses')">
          <i class="fa-solid fa-book-bookmark"></i>
          <span>Môn Học & Lịch Dạy</span>
        </li>
        <div class="menu-category">Đào Tạo & Học Tập</div>
        <li class="nav-link" onclick="app.switchSection('students-list')">
          <i class="fa-solid fa-users"></i>
          <span>Danh Sách Sinh Viên</span>
        </li>
        <li class="nav-link" onclick="app.switchSection('schedule')">
          <i class="fa-solid fa-calendar-days"></i>
          <span>Thời Khóa Biểu</span>
        </li>
        <li class="nav-link" onclick="app.switchSection('grading')">
          <i class="fa-solid fa-file-pen"></i>
          <span>Quản Lý Điểm Số</span>
        </li>
        <div class="menu-category">Cá Nhân</div>
        <li class="nav-link" onclick="app.switchSection('profile')">
          <i class="fa-solid fa-id-badge"></i>
          <span>Hồ Sơ Cá Nhân</span>
        </li>
      `;
    } else if (vaiTro === 'Giảng viên') {
      html += `
        <div class="menu-category">Giảng Dạy & Lớp Học</div>
        <li class="nav-link active" onclick="app.switchSection('schedule')">
          <i class="fa-solid fa-calendar-days"></i>
          <span>Lịch Dạy Trong Tuần</span>
        </li>
        <li class="nav-link" onclick="app.switchSection('students-list')">
          <i class="fa-solid fa-users"></i>
          <span>Danh Sách Sinh Viên</span>
        </li>
        <li class="nav-link" onclick="app.switchSection('attendance')">
          <i class="fa-solid fa-clipboard-user"></i>
          <span>Điểm Danh Chuyên Cần</span>
        </li>
        <li class="nav-link" onclick="app.switchSection('grading')">
          <i class="fa-solid fa-file-pen"></i>
          <span>Sổ Điểm Môn Học</span>
        </li>
        <div class="menu-category">Tài Khoản</div>
        <li class="nav-link" onclick="app.switchSection('profile')">
          <i class="fa-solid fa-id-badge"></i>
          <span>Hồ Sơ Giảng Viên</span>
        </li>
      `;
    } else {
      html += `
        <div class="menu-category">Học Tập & Đào Tạo</div>
        <li class="nav-link active" onclick="app.switchSection('schedule')">
          <i class="fa-solid fa-calendar-days"></i>
          <span>Thời Khóa Biểu Cá Nhân</span>
        </li>
        <li class="nav-link" onclick="app.switchSection('registration')">
          <i class="fa-solid fa-folder-plus"></i>
          <span>Đăng Ký Học Phần</span>
        </li>
        <li class="nav-link" onclick="app.switchSection('my-grades')">
          <i class="fa-solid fa-award"></i>
          <span>Kết Quả Học Tập</span>
        </li>
        <li class="nav-link" onclick="app.switchSection('tuition')">
          <i class="fa-solid fa-wallet"></i>
          <span>Tra Cứu Học Phí</span>
        </li>
        <div class="menu-category">Tài Khoản</div>
        <li class="nav-link" onclick="app.switchSection('profile')">
          <i class="fa-solid fa-id-badge"></i>
          <span>Hồ Sơ Sinh Viên</span>
        </li>
      `;
    }
    menuEl.innerHTML = html;
  },

  switchSection(sectionId) {
    this.phanKhuHienTai = sectionId;

    const links = document.querySelectorAll('.nav-link');
    links.forEach(l => l.classList.remove('active'));
    links.forEach(l => {
      if (l.getAttribute('onclick') && l.getAttribute('onclick').includes(sectionId)) {
        l.classList.add('active');
      }
    });

    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.classList.remove('open');
    const overlay = document.getElementById('sidebar-overlay');
    if (overlay) overlay.classList.remove('show');

    const sections = document.querySelectorAll('.content-view');
    sections.forEach(s => s.style.display = 'none');

    const target = document.getElementById(`view-${sectionId}`);
    if (target) target.style.display = 'block';

    this.updateHeaderTitle(sectionId);

    switch (sectionId) {
      case 'dashboard': this.renderDashboard(); break;
      case 'profile': this.renderProfile(); break;
      case 'students-list': this.loadStudentList(); break;
      case 'schedule': this.loadScheduleView(); break;
      case 'attendance': this.loadAttendanceView(); break;
      case 'grading': this.loadGradingView(); break;
      case 'registration': this.loadRegistrationView(); break;
      case 'my-grades': this.loadMyGradesView(); break;
      case 'tuition': this.loadTuitionView(); break;
      case 'admin-users': this.loadAdminUsersView(); break;
      case 'admin-courses': this.loadAdminCoursesView(); break;
    }
  },

  updateHeaderTitle(sectionId) {
    const titles = {
      dashboard: ['Tổng Quan Hệ Thống', 'Thống kê hoạt động đào tạo và kết quả học tập'],
      profile: ['Hồ Sơ Cá Nhân', 'Quản lý và cập nhật thông tin tài khoản'],
      'students-list': ['Danh Sách Sinh Viên', 'Tra cứu danh sách hồ sơ sinh viên'],
      schedule: ['Thời Khóa Biểu', 'Lịch học tập và giảng dạy theo tuần'],
      attendance: ['Điểm Danh Chuyên Cần', 'Theo dõi và chấm chuyên cần sinh viên'],
      grading: [this.nguoiDungHienTai?.vai_trò === 'Quản trị viên' ? 'Quản Lý Điểm Số Toàn Trường' : 'Sổ Điểm Môn Học', this.nguoiDungHienTai?.vai_trò === 'Quản trị viên' ? 'Tra cứu, điều chỉnh điểm và kết quả học tập của tất cả sinh viên' : 'Quản lý và cập nhật điểm số môn học phụ trách'],
      registration: ['Đăng Ký Học Phần', 'Cổng đăng ký tín chỉ mở trong kỳ'],
      'my-grades': ['Kết Quả Học Tập', 'Tra cứu bảng điểm chi tiết và GPA'],
      tuition: ['Cổng Học Phí', 'Tra cứu thông tin học phí và biên lai'],
      'admin-users': ['Quản Lý Tài Khoản & Phân Quyền', 'Thêm, sửa, cấp quyền và quản lý tài khoản người dùng'],
      'admin-courses': ['Môn Học & Lịch Dạy', 'Quản lý danh mục đào tạo và phân công giảng dạy']
    };

    const [heading, sub] = titles[sectionId] || ['Hệ Thống Đào Tạo', 'Quản lý sinh viên'];
    document.getElementById('page-heading').innerText = heading;
    document.getElementById('page-subheading').innerText = sub;
  },

  // -------------------------------------------------------------
  // 1. DASHBOARD & BIỂU ĐỒ
  // -------------------------------------------------------------
  async renderDashboard() {
    const user = this.nguoiDungHienTai;
    if (!user) return;

    document.getElementById('welcome-title').innerText = `Xin chào, ${user.họ_tên}!`;
    document.getElementById('welcome-sub').innerText = user.vai_trò === 'Quản trị viên'
      ? 'Hệ thống phân quyền đang hoạt động với đầy đủ quyền quản trị đào tạo.'
      : (user.vai_trò === 'Giảng viên' ? 'Kiểm tra lịch giảng dạy, điểm danh và sổ điểm các môn phụ trách.' : 'Xem thời khóa biểu, tiến độ học tập và đăng ký các môn học trong kỳ.');

    try {
      const data = await this.goiApi('/api/thong-ke/tong-quan');
      document.getElementById('stat-teachers').innerText = data.số_giảng_viên;
      document.getElementById('stat-students').innerText = data.số_sinh_viên;
      document.getElementById('stat-courses').innerText = data.số_môn_học;
      document.getElementById('stat-schedules').innerText = data.số_lịch_dạy;

      this.renderDashboardChart(data.phân_bố_khoa, data.số_môn_học);
    } catch (e) {}
  },

  renderDashboardChart(phanBoKhoa = [], tongMon = 0) {
    const canvas = document.getElementById('dash-chart-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
    const palette = ['#f97316', '#3b82f6', '#10b981', '#8b5cf6', '#f59e0b', '#06b6d4', '#ec4899', '#6366f1'];

    if (!phanBoKhoa || phanBoKhoa.length === 0 || tongMon === 0) {
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.font = '13px Inter';
      ctx.fillStyle = isDark ? '#94a3b8' : '#64748b';
      ctx.fillText('Chưa có dữ liệu môn học', canvas.width / 2, canvas.height / 2);
      return;
    }

    const data = phanBoKhoa.map((item, idx) => ({
      label: item.khoa,
      count: item.số_lượng,
      percent: item.tỷ_lệ,
      color: palette[idx % palette.length],
    }));

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const outerRadius = 88;
    const innerRadius = 54;
    let currentAngle = -Math.PI / 2;

    data.forEach(item => {
      const sliceAngle = (item.count / tongMon) * (2 * Math.PI);
      const endAngle = currentAngle + sliceAngle;

      ctx.beginPath();
      ctx.arc(centerX, centerY, outerRadius, currentAngle, endAngle - (data.length > 1 ? 0.03 : 0));
      ctx.arc(centerX, centerY, innerRadius, endAngle - (data.length > 1 ? 0.03 : 0), currentAngle, true);
      ctx.closePath();
      ctx.fillStyle = item.color;
      ctx.fill();

      currentAngle = endAngle;
    });

    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.font = '11px Inter';
    ctx.fillStyle = isDark ? '#94a3b8' : '#64748b';
    ctx.fillText('Tổng số môn', centerX, centerY - 10);

    ctx.font = 'bold 20px Plus Jakarta Sans';
    ctx.fillStyle = isDark ? '#fff7ed' : '#0f172a';
    ctx.fillText(`${tongMon}`, centerX, centerY + 12);

    const legendEl = document.getElementById('dash-chart-legend');
    if (legendEl) {
      legendEl.innerHTML = data.map(item => `
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 7px 12px; border-radius: var(--radius-sm); background: var(--bg-subtle); border: 1px solid var(--border-subtle);">
          <div style="display: flex; align-items: center; gap: 10px; min-width: 0;">
            <div style="width: 12px; height: 12px; border-radius: 3px; background: ${item.color}; flex-shrink: 0;"></div>
            <span style="font-size: 13px; font-weight: 600; color: var(--text-main); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${item.label}</span>
          </div>
          <div style="display: flex; align-items: center; gap: 8px; flex-shrink: 0;">
            <span style="font-size: 12.5px; font-weight: 700; color: var(--text-muted);">${item.count} môn</span>
            <span class="badge-role" style="background: rgba(249, 115, 22, 0.12); color: var(--primary); font-size: 11px; padding: 1px 6px; font-weight: 700;">${item.percent}%</span>
          </div>
        </div>
      `).join('');
    }
  },

  // -------------------------------------------------------------
  // 2. HỒ SƠ CÁ NHÂN & ẢNH ĐẠI DIỆN
  // -------------------------------------------------------------
  async renderProfile() {
    try {
      const res = await this.goiApi('/api/ho-so');
      const user = res.hồ_sơ;
      this.nguoiDungHienTai = user;

      const avatarImg = document.getElementById('profile-avatar-img');
      const avatarInitials = document.getElementById('profile-avatar-initials');
      const btnRemove = document.getElementById('btn-remove-avatar');

      if (user.ảnh_đại_diện) {
        if (avatarImg) {
          avatarImg.src = user.ảnh_đại_diện;
          avatarImg.style.display = 'block';
        }
        if (avatarInitials) avatarInitials.style.display = 'none';
        if (btnRemove) btnRemove.style.display = 'inline-flex';
      } else {
        if (avatarImg) {
          avatarImg.src = '';
          avatarImg.style.display = 'none';
        }
        if (avatarInitials) {
          avatarInitials.innerText = user.họ_tên ? user.họ_tên.split(' ').pop().charAt(0).toUpperCase() : 'U';
          avatarInitials.style.display = 'block';
        }
        if (btnRemove) btnRemove.style.display = 'none';
      }

      document.getElementById('profile-name-text').innerText = user.họ_tên || '';
      const codeEl = document.getElementById('profile-code-text');
      if (codeEl) codeEl.innerText = user.mã_số ? `Mã: ${user.mã_số}` : '';

      const rBadge = document.getElementById('profile-role-text');
      rBadge.innerText = user.vai_trò || '';
      rBadge.className = `badge-role badge-${this.chuanHoaClassVaiTro(user.vai_trò)}`;

      document.getElementById('prof-fullname').value = user.họ_tên || '';
      document.getElementById('prof-title').value = user.chức_danh || '';
      document.getElementById('prof-age').value = user.tuổi || '';
      document.getElementById('prof-department').value = user.khoa || '';
      document.getElementById('prof-email').value = user.email || '';
      document.getElementById('prof-phone').value = user.số_điện_thoại || '';
    } catch (e) {}
  },

  handleAvatarUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      this.toast('error', 'Kích thước ảnh quá lớn! Vui lòng chọn ảnh dưới 5MB.');
      event.target.value = '';
      return;
    }

    if (!file.type.startsWith('image/')) {
      this.toast('error', 'Vui lòng chọn file hình ảnh hợp lệ (PNG, JPG, JPEG, WEBP)!');
      event.target.value = '';
      return;
    }

    const reader = new FileReader();
    reader.onload = async (e) => {
      const base64 = e.target.result;
      try {
        const ketQua = await this.goiApi('/api/ho-so/anh-dai-dien', 'POST', {
          ảnh_đại_diện: base64,
        });
        this.nguoiDungHienTai = ketQua.hồ_sơ;
        this.toast('success', ketQua.thông_báo);
        this.renderAppForUser(this.nguoiDungHienTai);
        this.renderProfile();
      } catch (err) {}
      event.target.value = '';
    };
    reader.readAsDataURL(file);
  },

  async removeAvatar() {
    try {
      const ketQua = await this.goiApi('/api/ho-so/anh-dai-dien', 'DELETE');
      this.nguoiDungHienTai = ketQua.hồ_sơ;
      this.toast('info', ketQua.thông_báo);
      this.renderAppForUser(this.nguoiDungHienTai);
      this.renderProfile();
    } catch (e) {}
  },

  async saveProfile(event) {
    event.preventDefault();
    const duLieu = {
      họ_tên: document.getElementById('prof-fullname').value.trim(),
      chức_danh: document.getElementById('prof-title').value.trim(),
      tuổi: parseInt(document.getElementById('prof-age').value) || 20,
      khoa: document.getElementById('prof-department').value.trim(),
      email: document.getElementById('prof-email').value.trim(),
      số_điện_thoại: document.getElementById('prof-phone').value.trim(),
    };

    try {
      const ketQua = await this.goiApi('/api/ho-so', 'PUT', duLieu);
      this.nguoiDungHienTai = ketQua.hồ_sơ;
      this.toast('success', ketQua.thông_báo);
      this.renderAppForUser(this.nguoiDungHienTai);
      this.renderProfile();
    } catch (e) {}
  },

  // -------------------------------------------------------------
  // 3. DANH SÁCH SINH VIÊN (GIẢNG VIÊN & ADMIN)
  // -------------------------------------------------------------
  async loadStudentList() {
    const tuKhoa = (document.getElementById('search-student-input')?.value || '').trim();
    const tbody = document.getElementById('student-table-body');
    if (!tbody) return;

    try {
      const res = await this.goiApi(`/api/nguoi-dung/sinh-vien?tu_khoa=${encodeURIComponent(tuKhoa)}`);
      const danhSach = res.danh_sách || [];

      if (danhSach.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;color:var(--text-dim);padding:30px;">Không tìm thấy sinh viên phù hợp.</td></tr>`;
        return;
      }

      tbody.innerHTML = danhSach.map(s => `
        <tr ondblclick="app.openStudentTranscript('${s.định_danh}')" style="cursor:pointer;" title="Nháy đúp chuột để xem toàn bộ bảng điểm của ${s.họ_tên}">
          <td><strong style="color:var(--primary);">${s.mã_số || 'SV-N/A'}</strong></td>
          <td>
            <div style="display:flex;align-items:center;gap:12px;">
              <div class="user-avatar-sm" style="width:36px;height:36px;font-size:13px;flex-shrink:0;${s.ảnh_đại_diện ? 'cursor:pointer;border:2px solid var(--primary);' : ''}" ${s.ảnh_đại_diện ? `onclick="event.stopPropagation(); app.previewAvatar('${s.định_danh}')" title="Xem ảnh"` : ''}>
                ${s.ảnh_đại_diện ? `<img src="${s.ảnh_đại_diện}" alt="${s.họ_tên}">` : (s.họ_tên || 'S').split(' ').pop().charAt(0)}
              </div>
              <div>
                <strong style="display:block;font-size:13.5px;">${s.họ_tên}</strong>
              </div>
            </div>
          </td>
          <td><span class="badge-role badge-student">${s.lớp || s.chức_danh || 'K66'}</span></td>
          <td>${s.khoa || 'Công nghệ thông tin'}</td>
          <td>${s.email || '-'}</td>
          <td>${s.số_điện_thoại || '-'}</td>
          <td>${s.tuổi || 20}</td>
          <td>
            <button onclick="event.stopPropagation(); app.openStudentTranscript('${s.định_danh}')" class="btn btn-secondary btn-sm" style="padding:5px 10px;font-size:12px;" title="Xem toàn bộ bảng điểm">
              <i class="fa-solid fa-graduation-cap" style="color:var(--primary);"></i> Bảng Điểm
            </button>
          </td>
        </tr>
      `).join('');
    } catch (e) {}
  },

  // -------------------------------------------------------------
  // 4. QUẢN TRỊ TÀI KHOẢN & PHÂN QUYỀN (ADMIN)
  // -------------------------------------------------------------
  setAdminRoleFilter(role, btn) {
    this.boLocVaiTroAdmin = role;
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
    this.loadAdminUsersView();
  },

  async loadAdminUsersView() {
    const tbody = document.getElementById('admin-users-table-body');
    if (!tbody) return;

    const tuKhoa = (document.getElementById('admin-search-user-input')?.value || '').trim();
    let url = `/api/nguoi-dung?tu_khoa=${encodeURIComponent(tuKhoa)}`;
    if (this.boLocVaiTroAdmin !== 'all') {
      const vaiTroVi = this.chuanHoaMaVaiTro(this.boLocVaiTroAdmin);
      url += `&vai_tro=${encodeURIComponent(vaiTroVi)}`;
    }

    try {
      const res = await this.goiApi(url);
      const danhSach = res.danh_sách || [];

      if (danhSach.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--text-dim);padding:30px;">Không có tài khoản nào phù hợp.</td></tr>`;
        return;
      }

      tbody.innerHTML = danhSach.map(u => `
        <tr>
          <td><strong style="color:var(--text-dim);font-size:12px;">${u.mã_số || u.định_danh}</strong></td>
          <td>
            <div style="display:flex;align-items:center;gap:12px;">
              <div class="user-avatar-sm" style="width:36px;height:36px;font-size:13px;flex-shrink:0;${u.ảnh_đại_diện ? 'cursor:pointer;border:2px solid var(--primary);' : ''}" ${u.ảnh_đại_diện ? `onclick="app.previewAvatar('${u.định_danh}')" title="Xem ảnh"` : ''}>
                ${u.ảnh_đại_diện ? `<img src="${u.ảnh_đại_diện}" alt="${u.họ_tên}">` : (u.họ_tên || 'U').split(' ').pop().charAt(0)}
              </div>
              <div>
                <strong style="display:block;font-size:13.5px;">${u.họ_tên}</strong>
                <span style="font-size:12px;color:var(--text-dim);">@${u.tên_đăng_nhập}</span>
              </div>
            </div>
          </td>
          <td><span class="badge-role badge-${this.chuanHoaClassVaiTro(u.vai_trò)}">${u.vai_trò}</span></td>
          <td>${u.khoa || '-'}</td>
          <td>${u.email || '-'}</td>
          <td>
            ${u.trạng_thái === 'Đã khóa' ? 
              '<span class="badge-role badge-admin"><i class="fa-solid fa-lock"></i> Đã khóa</span>' : 
              '<span class="badge-role badge-student"><i class="fa-solid fa-circle-check"></i> Hoạt động</span>'
            }
          </td>
          <td>
            <div style="display:flex;gap:6px;">
              <button onclick="app.openEditUserModal('${u.định_danh}')" class="btn btn-secondary btn-sm" title="Chỉnh sửa thông tin & phân quyền">
                <i class="fa-solid fa-pen-to-square" style="color:var(--primary);"></i> Sửa
              </button>
              <button onclick="app.toggleUserLock('${u.định_danh}')" class="btn btn-secondary btn-sm" title="${u.trạng_thái === 'Đã khóa' ? 'Mở khóa' : 'Khóa tài khoản'}">
                <i class="fa-solid ${u.trạng_thái === 'Đã khóa' ? 'fa-lock-open' : 'fa-lock'}" style="color:${u.trạng_thái === 'Đã khóa' ? '#10b981' : '#f59e0b'};"></i>
              </button>
              <button onclick="app.deleteUser('${u.định_danh}')" class="btn btn-danger btn-sm" ${u.định_danh === this.nguoiDungHienTai?.định_danh ? 'disabled' : ''} title="Xóa tài khoản">
                <i class="fa-solid fa-trash"></i>
              </button>
            </div>
          </td>
        </tr>
      `).join('');
    } catch (e) {}
  },

  showCreateUserModal() {
    document.getElementById('form-create-user').reset();
    this.openModal('modal-create-user');
  },

  async handleCreateUser(event) {
    event.preventDefault();
    const vaiTroVal = document.getElementById('new-u-role').value;
    const duLieu = {
      tên_đăng_nhập: document.getElementById('new-u-username').value.trim(),
      mật_khẩu: document.getElementById('new-u-password').value.trim(),
      vai_trò: this.chuanHoaMaVaiTro(vaiTroVal),
      họ_tên: document.getElementById('new-u-fullname').value.trim(),
      mã_số: document.getElementById('new-u-code').value.trim(),
      khoa: document.getElementById('new-u-department').value.trim(),
      email: document.getElementById('new-u-email').value.trim(),
      số_điện_thoại: document.getElementById('new-u-phone').value.trim(),
    };

    try {
      const ketQua = await this.goiApi('/api/nguoi-dung', 'POST', duLieu);
      this.closeModal('modal-create-user');
      this.toast('success', ketQua.thông_báo);
      this.loadAdminUsersView();
    } catch (e) {}
  },

  async openEditUserModal(dinhDanh) {
    try {
      const res = await this.goiApi('/api/nguoi-dung');
      const user = (res.danh_sách || []).find(u => u.định_danh === dinhDanh);
      if (!user) return;

      document.getElementById('edit-u-id').value = user.định_danh;
      document.getElementById('edit-u-username').value = user.tên_đăng_nhập;
      document.getElementById('edit-u-fullname').value = user.họ_tên;
      document.getElementById('edit-u-role').value = this.chuanHoaClassVaiTro(user.vai_trò);
      document.getElementById('edit-u-code').value = user.mã_số || '';
      document.getElementById('edit-u-department').value = user.khoa || '';
      document.getElementById('edit-u-email').value = user.email || '';
      document.getElementById('edit-u-phone').value = user.số_điện_thoại || '';
      document.getElementById('edit-u-status').value = user.trạng_thái === 'Đã khóa' ? 'locked' : 'active';
      document.getElementById('edit-u-newpass').value = '';

      this.openModal('modal-edit-user');
    } catch (e) {}
  },

  async handleUpdateUser(event) {
    event.preventDefault();
    const dinhDanh = document.getElementById('edit-u-id').value;
    const roleVal = document.getElementById('edit-u-role').value;
    const statusVal = document.getElementById('edit-u-status').value;

    const duLieu = {
      họ_tên: document.getElementById('edit-u-fullname').value.trim(),
      vai_trò: this.chuanHoaMaVaiTro(roleVal),
      mã_số: document.getElementById('edit-u-code').value.trim(),
      khoa: document.getElementById('edit-u-department').value.trim(),
      email: document.getElementById('edit-u-email').value.trim(),
      số_điện_thoại: document.getElementById('edit-u-phone').value.trim(),
      trạng_thái: statusVal === 'locked' ? 'Đã khóa' : 'Hoạt động',
      mật_khẩu_mới: document.getElementById('edit-u-newpass').value.trim(),
    };

    try {
      const ketQua = await this.goiApi(`/api/nguoi-dung/${dinhDanh}`, 'PUT', duLieu);
      if (this.nguoiDungHienTai?.định_danh === dinhDanh) {
        this.nguoiDungHienTai = ketQua.người_dùng;
        this.renderAppForUser(this.nguoiDungHienTai);
      }
      this.closeModal('modal-edit-user');
      this.toast('success', ketQua.thông_báo);
      this.loadAdminUsersView();
    } catch (e) {}
  },

  async toggleUserLock(dinhDanh) {
    try {
      const ketQua = await this.goiApi(`/api/nguoi-dung/${dinhDanh}/khoa`, 'PATCH');
      this.toast('info', ketQua.thông_báo);
      this.loadAdminUsersView();
    } catch (e) {}
  },

  async deleteUser(dinhDanh) {
    if (!confirm('Bạn có chắc chắn muốn xóa tài khoản này khỏi hệ thống?')) return;
    try {
      const ketQua = await this.goiApi(`/api/nguoi-dung/${dinhDanh}`, 'DELETE');
      this.toast('success', ketQua.thông_báo);
      this.loadAdminUsersView();
    } catch (e) {}
  },

  // -------------------------------------------------------------
  // 5. THỜI KHÓA BIỂU
  // -------------------------------------------------------------
  async loadScheduleView() {
    const week = document.getElementById('filter-week-select')?.value;
    const day = document.getElementById('filter-day-select')?.value;
    const container = document.getElementById('schedule-cards-container');
    const titleEl = document.getElementById('schedule-card-title');
    if (!container) return;

    let url = '/api/lich-hoc';
    const params = [];
    if (week) params.push(`tuan=${week}`);
    if (day) params.push(`thu=${encodeURIComponent(day)}`);
    if (params.length > 0) url += `?${params.join('&')}`;

    const user = this.nguoiDungHienTai;
    if (user?.vai_trò === 'Quản trị viên') {
      if (titleEl) titleEl.innerHTML = `<i class="fa-solid fa-calendar-days" style="color:var(--primary);"></i> Thời Khóa Biểu Toàn Trường (Quản Trị)`;
    } else if (user?.vai_trò === 'Giảng viên') {
      if (titleEl) titleEl.innerHTML = `<i class="fa-solid fa-calendar-days" style="color:var(--primary);"></i> Lịch Giảng Dạy Của Tôi`;
    } else {
      if (titleEl) titleEl.innerHTML = `<i class="fa-solid fa-calendar-days" style="color:var(--primary);"></i> Thời Khóa Biểu Cá Nhân`;
    }

    try {
      const res = await this.goiApi(url);
      const list = res.danh_sách || [];

      if (list.length === 0) {
        if (res.chưa_đăng_ký_môn) {
          container.innerHTML = `
            <div class="card" style="padding: 36px 20px; text-align: center; grid-column: 1 / -1;">
              <i class="fa-solid fa-folder-open" style="font-size: 38px; color: var(--primary); margin-bottom: 12px; display: inline-block;"></i>
              <h4 style="font-size: 16px; font-weight: 700; margin-bottom: 6px;">Bạn chưa đăng ký môn học nào</h4>
              <p style="color: var(--text-muted); font-size: 13.5px; margin-bottom: 16px;">Vui lòng chuyển qua mục Đăng ký học phần để chọn các môn học trong kỳ.</p>
              <button onclick="app.switchSection('registration')" class="btn btn-primary btn-sm">
                <i class="fa-solid fa-folder-plus"></i> Đăng Ký Học Phần Ngay
              </button>
            </div>
          `;
        } else {
          container.innerHTML = `
            <div class="card" style="padding: 36px 20px; text-align: center; grid-column: 1 / -1;">
              <i class="fa-solid fa-calendar-xmark" style="font-size: 38px; color: var(--text-dim); margin-bottom: 12px; display: inline-block;"></i>
              <h4 style="font-size: 16px; font-weight: 700; margin-bottom: 6px;">Không có lịch học nào phù hợp</h4>
              <p style="color: var(--text-muted); font-size: 13.5px;">Hãy thử chọn tuần khác hoặc chọn "Tất cả các tuần" / "Tất cả các thứ".</p>
            </div>
          `;
        }
        return;
      }

      container.innerHTML = list.map(s => `
        <div class="card" style="display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px; gap: 8px;">
              <h4 style="font-size:15px; font-weight:700; line-height: 1.3;">${s.tên_môn}</h4>
              <span class="badge-role badge-teacher" style="flex-shrink: 0;">${s.mã_môn}</span>
            </div>
            <div style="display:flex; align-items:center; gap:6px; font-size:13px; color:var(--primary); font-weight:600; margin-bottom:12px;">
              <i class="fa-solid fa-clock"></i> ${s.thứ} (${s.giờ_bắt_đầu} - ${s.giờ_kết_thúc})
            </div>
          </div>
          <div style="font-size:13px; color:var(--text-muted); display:flex; flex-direction:column; gap:7px; border-top: 1px solid var(--border-subtle); padding-top: 10px;">
            <span><i class="fa-solid fa-location-dot" style="width:18px; color: var(--primary);"></i> Phòng: <strong>${s.phòng_học}</strong></span>
            <span><i class="fa-solid fa-chalkboard-user" style="width:18px; color: var(--primary);"></i> Giảng viên: <strong>${s.tên_giảng_viên}</strong></span>
            <span><i class="fa-solid fa-calendar-week" style="width:18px; color: var(--primary);"></i> Tuần học số: <strong>${s.tuần}</strong></span>
          </div>
        </div>
      `).join('');
    } catch (e) {}
  },

  async showCreateScheduleModal() {
    const cSelect = document.getElementById('sch-course-select');
    const tSelect = document.getElementById('sch-teacher-select');

    try {
      const [resMon, resGV] = await Promise.all([
        this.goiApi('/api/mon-hoc'),
        this.goiApi('/api/nguoi-dung/giang-vien')
      ]);

      if (cSelect) {
        cSelect.innerHTML = (resMon.danh_sách || []).map(c => `<option value="${c.định_danh}">${c.tên_môn} (${c.mã_môn})</option>`).join('');
      }
      if (tSelect) {
        tSelect.innerHTML = (resGV.danh_sách || []).map(t => `<option value="${t.định_danh}">${t.họ_tên} (${t.mã_số || 'GV'})</option>`).join('');
      }

      this.openModal('modal-create-schedule');
    } catch (e) {}
  },

  async handleCreateSchedule(event) {
    event.preventDefault();
    const duLieu = {
      định_danh_môn: document.getElementById('sch-course-select').value,
      định_danh_giảng_viên: document.getElementById('sch-teacher-select').value,
      phòng_học: document.getElementById('sch-room').value.trim(),
      thứ: document.getElementById('sch-day').value,
      tuần: parseInt(document.getElementById('sch-week').value) || 1,
      giờ_bắt_đầu: document.getElementById('sch-start').value.trim(),
      giờ_kết_thúc: document.getElementById('sch-end').value.trim(),
    };

    try {
      const ketQua = await this.goiApi('/api/lich-hoc', 'POST', duLieu);
      this.closeModal('modal-create-schedule');
      this.toast('success', ketQua.thông_báo);
      this.switchSection('schedule');
    } catch (e) {}
  },

  // -------------------------------------------------------------
  // 6. ĐIỂM DANH CHUYÊN CẦN (GIẢNG VIÊN & ADMIN)
  // -------------------------------------------------------------
  async loadAttendanceView() {
    const select = document.getElementById('att-schedule-select');
    if (!select) return;

    try {
      const res = await this.goiApi('/api/lich-hoc');
      const list = res.danh_sách || [];

      select.innerHTML = '<option value="">-- Chọn lịch dạy / lớp học phần --</option>' + 
        list.map(s => `<option value="${s.định_danh}">${s.tên_môn} - ${s.mã_môn} (${s.thứ} - Tuần ${s.tuần})</option>`).join('');

      this.loadStudentsForAttendance();
    } catch (e) {}
  },

  async loadStudentsForAttendance() {
    const schedId = document.getElementById('att-schedule-select')?.value;
    const dateVal = document.getElementById('att-date-input')?.value || new Date().toISOString().split('T')[0];
    const tbody = document.getElementById('attendance-table-body');
    if (!tbody) return;

    if (!schedId) {
      tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:var(--text-dim);padding:24px;">Vui lòng chọn lớp học để tiến hành điểm danh.</td></tr>`;
      return;
    }

    try {
      const res = await this.goiApi(`/api/diem-danh?dinh_danh_lich=${schedId}&ngay=${dateVal}`);
      const list = res.danh_sách || [];

      if (list.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:var(--text-dim);padding:24px;">Chưa có sinh viên nào đăng ký học phần này.</td></tr>`;
        return;
      }

      tbody.innerHTML = list.map(s => `
        <tr>
          <td><strong style="color:var(--primary);">${s.mã_số || 'SV001'}</strong></td>
          <td>
            <div style="display:flex;align-items:center;gap:10px;">
              <div class="user-avatar-sm" style="width:30px;height:30px;font-size:11px;${s.ảnh_đại_diện ? 'cursor:pointer;border:1.5px solid var(--primary);' : ''}" ${s.ảnh_đại_diện ? `onclick="app.previewAvatar('${s.định_danh}')" title="Xem ảnh"` : ''}>
                ${s.ảnh_đại_diện ? `<img src="${s.ảnh_đại_diện}" alt="${s.họ_tên}">` : (s.họ_tên || 'S').split(' ').pop().charAt(0)}
              </div>
              <span style="${s.ảnh_đại_diện ? 'cursor:pointer;' : ''}" ${s.ảnh_đại_diện ? `onclick="app.previewAvatar('${s.định_danh}')"` : ''}>${s.họ_tên}</span>
            </div>
          </td>
          <td>
            <select id="att-status-${s.định_danh}" class="form-input" style="width:160px;padding:6px 10px;">
              <option value="Có mặt" ${s.trạng_thái === 'Có mặt' ? 'selected' : ''}>✅ Có mặt</option>
              <option value="Đi muộn" ${s.trạng_thái === 'Đi muộn' ? 'selected' : ''}>⏰ Đi muộn</option>
              <option value="Vắng có phép" ${s.trạng_thái === 'Vắng có phép' ? 'selected' : ''}>📝 Vắng có phép</option>
              <option value="Vắng không phép" ${s.trạng_thái === 'Vắng không phép' ? 'selected' : ''}>❌ Vắng không phép</option>
            </select>
          </td>
          <td>
            <input type="text" id="att-note-${s.định_danh}" class="form-input" value="${s.ghi_chú || ''}" placeholder="Ghi chú nếu có..." style="padding:6px 10px;">
          </td>
        </tr>
      `).join('');
    } catch (e) {}
  },

  markAllPresent() {
    const selects = document.querySelectorAll('[id^="att-status-"]');
    selects.forEach(s => s.value = 'Có mặt');
    this.toast('success', 'Đã chọn tất cả sinh viên có mặt!');
  },

  async submitAttendance() {
    const schedId = document.getElementById('att-schedule-select')?.value;
    const dateVal = document.getElementById('att-date-input')?.value;

    if (!schedId) {
      this.toast('warning', 'Vui lòng chọn lớp học để lưu điểm danh.');
      return;
    }

    const selects = document.querySelectorAll('[id^="att-status-"]');
    const records = Array.from(selects).map(sel => {
      const svId = sel.id.replace('att-status-', '');
      const noteInput = document.getElementById(`att-note-${svId}`);
      return {
        định_danh_sinh_viên: svId,
        trạng_thái: sel.value,
        ghi_chú: noteInput ? noteInput.value : '',
      };
    });

    try {
      const ketQua = await this.goiApi('/api/diem-danh', 'POST', {
        định_danh_lịch_học: schedId,
        ngày: dateVal || new Date().toISOString().split('T')[0],
        danh_sách: records,
      });
      this.toast('success', ketQua.thông_báo);
    } catch (e) {}
  },

  // -------------------------------------------------------------
  // 7. SỔ ĐIỂM & QUẢN LÝ ĐIỂM SỐ
  // -------------------------------------------------------------
  async loadGradingView() {
    const select = document.getElementById('grading-course-select');
    if (!select) return;

    try {
      const res = await this.goiApi('/api/mon-hoc');
      const list = res.danh_sách || [];

      select.innerHTML = '<option value="">-- Chọn môn học --</option>' + 
        list.map(c => `<option value="${c.định_danh}">${c.tên_môn} (${c.mã_môn}) - ${c.số_tín_chỉ} TC</option>`).join('');

      this.loadGradesForCourse();
    } catch (e) {}
  },

  async loadGradesForCourse() {
    const courseId = document.getElementById('grading-course-select')?.value;
    const tbody = document.getElementById('grading-table-body');
    const deadlineBanner = document.getElementById('grade-deadline-banner');
    if (!tbody) return;

    if (!courseId) {
      if (deadlineBanner) deadlineBanner.style.display = 'none';
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--text-dim);padding:24px;">Vui lòng chọn môn học để xem và nhập điểm.</td></tr>`;
      return;
    }

    try {
      const res = await this.goiApi(`/api/diem-so/so-diem/${courseId}`);
      const mon = res.môn_học;
      const congDiem = res.cổng_điểm;
      const list = res.danh_sách || [];

      if (deadlineBanner) {
        deadlineBanner.style.display = 'block';
        deadlineBanner.innerHTML = `
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;padding:14px 18px;border-radius:var(--radius-md);background:var(--bg-subtle);border:1px solid var(--border-medium);margin-bottom:18px;">
            <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
              <div style="font-size:13.5px;">
                <i class="fa-solid fa-calendar-check" style="color:var(--primary);margin-right:6px;"></i>
                <span>Ngày mở nhập điểm: <strong>${congDiem.ngày_mở_nhập_điểm}</strong></span>
              </div>
              <div style="font-size:13.5px;">
                <i class="fa-solid fa-calendar-xmark" style="color:#ef4444;margin-right:6px;"></i>
                <span>Ngày chốt sổ điểm: <strong>${congDiem.ngày_chốt_điểm}</strong></span>
              </div>
              <div>
                ${congDiem.đã_khóa ? 
                  `<span class="badge-role badge-admin"><i class="fa-solid fa-lock"></i> ${congDiem.lý_do_khóa || 'Cổng điểm đã khóa'}</span>` : 
                  '<span class="badge-role badge-student"><i class="fa-solid fa-circle-check"></i> Đang mở nhập điểm</span>'
                }
              </div>
            </div>
            ${this.nguoiDungHienTai?.vai_trò === 'Quản trị viên' ? `
              <button onclick="app.openGradeDeadlineModal('${mon.định_danh}')" class="btn btn-secondary btn-sm">
                <i class="fa-solid fa-gear" style="color:var(--primary);"></i> Cài Đặt Hạn Nhập Điểm
              </button>
            ` : (!congDiem.được_phép_sửa ? '<span style="font-size:12px;color:#ef4444;font-weight:600;"><i class="fa-solid fa-triangle-exclamation"></i> Đã hết hạn sửa điểm</span>' : '')}
          </div>
        `;
      }

      const duocSua = congDiem.được_phép_sửa;

      tbody.innerHTML = list.map(s => `
        <tr>
          <td><strong style="color:var(--primary);">${s.mã_số || 'SV-001'}</strong></td>
          <td><strong>${s.họ_tên}</strong></td>
          <td>
            <input type="number" step="0.1" min="0" max="10" id="grade-mid-${s.định_danh_sinh_viên}" class="form-input" value="${s.điểm_giữa_kỳ ?? 8.0}" style="width:85px;padding:6px 10px;" oninput="app.recalcRowGrade('${s.định_danh_sinh_viên}')" ${!duocSua ? 'disabled' : ''}>
          </td>
          <td>
            <input type="number" step="0.1" min="0" max="10" id="grade-final-${s.định_danh_sinh_viên}" class="form-input" value="${s.điểm_cuối_kỳ ?? 8.5}" style="width:85px;padding:6px 10px;" oninput="app.recalcRowGrade('${s.định_danh_sinh_viên}')" ${!duocSua ? 'disabled' : ''}>
          </td>
          <td>
            <div style="display:flex;align-items:center;gap:8px;">
              <strong id="grade-total-${s.định_danh_sinh_viên}" style="font-size:15px;color:var(--primary);">${s.điểm_tổng_kết ?? '8.3'}</strong>
              <span id="grade-letter-${s.định_danh_sinh_viên}" class="badge-role badge-student">${s.điểm_chữ ?? 'B+'}</span>
            </div>
          </td>
          <td>
            <input type="text" id="grade-note-${s.định_danh_sinh_viên}" class="form-input" value="${s.nhận_xét || ''}" placeholder="Nhận xét..." ${!duocSua ? 'disabled' : ''}>
          </td>
          <td>
            <button onclick="app.saveSingleGrade('${s.định_danh_sinh_viên}', '${courseId}')" class="btn btn-primary btn-sm" ${!duocSua ? 'disabled style="opacity:0.5;cursor:not-allowed;"' : ''}>
              <i class="fa-solid fa-floppy-disk"></i> Lưu
            </button>
          </td>
        </tr>
      `).join('');
    } catch (e) {}
  },

  async recalcRowGrade(studentId) {
    const mid = parseFloat(document.getElementById(`grade-mid-${studentId}`)?.value);
    const fin = parseFloat(document.getElementById(`grade-final-${studentId}`)?.value);
    if (isNaN(mid) || isNaN(fin)) return;

    try {
      const res = await this.goiApi('/api/diem-so/tinh-nhanh', 'POST', {
        điểm_giữa_kỳ: mid,
        điểm_cuối_kỳ: fin,
      });

      const totalEl = document.getElementById(`grade-total-${studentId}`);
      const letterEl = document.getElementById(`grade-letter-${studentId}`);
      if (totalEl) totalEl.innerText = res.điểm_tổng_kết;
      if (letterEl) letterEl.innerText = res.điểm_chữ;
    } catch (e) {}
  },

  async saveSingleGrade(studentId, courseId) {
    const mid = parseFloat(document.getElementById(`grade-mid-${studentId}`)?.value) || 0;
    const fin = parseFloat(document.getElementById(`grade-final-${studentId}`)?.value) || 0;
    const note = document.getElementById(`grade-note-${studentId}`)?.value || '';

    try {
      const ketQua = await this.goiApi(`/api/diem-so/so-diem/${courseId}/sinh-vien/${studentId}`, 'PUT', {
        điểm_giữa_kỳ: mid,
        điểm_cuối_kỳ: fin,
        nhận_xét: note,
      });
      this.toast('success', ketQua.thông_báo);
    } catch (e) {}
  },

  async openGradeDeadlineModal(courseId) {
    try {
      const res = await this.goiApi('/api/mon-hoc');
      const course = (res.danh_sách || []).find(c => c.định_danh === courseId);
      if (!course) return;

      document.getElementById('dl-course-id').value = course.định_danh;
      document.getElementById('dl-course-name').innerText = `${course.tên_môn} (${course.mã_môn})`;
      document.getElementById('dl-start-date').value = course.ngày_mở_nhập_điểm || '2026-09-15';
      document.getElementById('dl-end-date').value = course.ngày_chốt_điểm || '2026-10-20';
      document.getElementById('dl-locked').value = course.khóa_nhập_điểm ? 'true' : 'false';

      this.openModal('modal-grade-deadline');
    } catch (e) {}
  },

  async handleSaveGradeDeadline(event) {
    event.preventDefault();
    const courseId = document.getElementById('dl-course-id').value;
    const duLieu = {
      ngày_mở_nhập_điểm: document.getElementById('dl-start-date').value,
      ngày_chốt_điểm: document.getElementById('dl-end-date').value,
      khóa_nhập_điểm: document.getElementById('dl-locked').value === 'true',
    };

    try {
      const ketQua = await this.goiApi(`/api/mon-hoc/${courseId}/han-nhap-diem`, 'PUT', duLieu);
      this.closeModal('modal-grade-deadline');
      this.toast('success', ketQua.thông_báo);
      this.loadGradesForCourse();
    } catch (e) {}
  },

  exportGradesToCSV() {
    const courseId = document.getElementById('grading-course-select')?.value;
    if (!courseId) {
      this.toast('warning', 'Vui lòng chọn môn học trước khi xuất file.');
      return;
    }

    if (this.cheDoHoatDong === 'fastapi') {
      window.location.href = `/api/diem-so/xuat-csv/${courseId}`;
      this.toast('success', 'Đang tải về file bảng điểm CSV...');
      return;
    }

    // Client-side export CSV trên GitHub Pages
    const mon = (this.duLieuCucBo?.môn_học || []).find(m => m.định_danh === courseId);
    let csv = `BẢNG ĐIỂM: ${mon?.tên_môn} (${mon?.mã_môn})\n`;
    csv += 'Mã SV,Họ và Tên,Điểm Giữa Kỳ (40%),Điểm Cuối Kỳ (60%),Điểm Tổng Kết,Điểm Chữ,Ghi Chú\n';

    const svList = (this.duLieuCucBo?.người_dùng || []).filter(u => u.vai_trò === 'Sinh viên');
    svList.forEach(s => {
      const dk = (this.duLieuCucBo?.đăng_ký_học_phần || []).find(d => d.định_danh_môn === courseId && d.định_danh_sinh_viên === s.định_danh);
      const mid = dk?.điểm_giữa_kỳ ?? 8.0;
      const fin = dk?.điểm_cuối_kỳ ?? 8.5;
      const total = +(mid * 0.4 + fin * 0.6).toFixed(1);
      const letter = this.tinhDiemChu(total);
      csv += `"${s.mã_số || ''}","${s.họ_tên}",${mid},${fin},${total},${letter},"${dk?.nhận_xét || ''}"\n`;
    });

    const blob = new Blob(["\uFEFF" + csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `BangDiem_${mon?.mã_môn || 'MonHoc'}.csv`;
    link.click();
    this.toast('success', 'Đã xuất file bảng điểm CSV thành công!');
  },

  // -------------------------------------------------------------
  // 8. ĐĂNG KÝ HỌC PHẦN (SINH VIÊN)
  // -------------------------------------------------------------
  async loadRegistrationView() {
    const tbody = document.getElementById('registration-table-body');
    if (!tbody) return;

    try {
      const res = await this.goiApi('/api/hoc-phan/danh-sach-mo');
      const list = res.danh_sách || [];

      tbody.innerHTML = list.map(c => `
        <tr>
          <td><strong style="color:var(--primary);">${c.mã_môn}</strong></td>
          <td><strong>${c.tên_môn}</strong></td>
          <td><span class="badge-role badge-student">${c.số_tín_chỉ} Tín chỉ</span></td>
          <td>${c.khoa}</td>
          <td style="color:var(--text-muted);font-size:12.5px;">${c.mô_tả || '-'}</td>
          <td>
            ${c.đã_đăng_ký ? `
              <button onclick="app.unregisterCourse('${c.định_danh}')" class="btn btn-danger btn-sm">
                <i class="fa-solid fa-trash-can"></i> Hủy Môn
              </button>
            ` : `
              <button onclick="app.registerCourse('${c.định_danh}')" class="btn btn-primary btn-sm">
                <i class="fa-solid fa-plus"></i> Đăng Ký
              </button>
            `}
          </td>
        </tr>
      `).join('');
    } catch (e) {}
  },

  async registerCourse(courseId) {
    try {
      const ketQua = await this.goiApi(`/api/hoc-phan/dang-ky/${courseId}`, 'POST');
      this.toast('success', ketQua.thông_báo);
      this.loadRegistrationView();
    } catch (e) {}
  },

  async unregisterCourse(courseId) {
    try {
      const ketQua = await this.goiApi(`/api/hoc-phan/huy-dang-ky/${courseId}`, 'DELETE');
      this.toast('info', ketQua.thông_báo);
      this.loadRegistrationView();
    } catch (e) {}
  },

  // -------------------------------------------------------------
  // 9. KẾT QUẢ HỌC TẬP & GPA CÁ NHÂN (SINH VIÊN)
  // -------------------------------------------------------------
  async loadMyGradesView() {
    const tbody = document.getElementById('my-grades-table-body');
    if (!tbody) return;

    try {
      const res = await this.goiApi('/api/diem-so/bang-diem-cua-toi');
      const myEnrollments = res.kết_quả_học_tập || [];
      const tongKet = res.tổng_kết || {};

      if (myEnrollments.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" style="text-align:center;color:var(--text-dim);padding:30px;">Bạn chưa có kết quả môn học nào.</td></tr>`;
        return;
      }

      tbody.innerHTML = myEnrollments.map(e => `
        <tr ondblclick="app.showGradeDetailModal('${e.định_danh}')" title="Nhấp đúp chuột để xem chi tiết thẻ điểm & nhận xét" style="cursor: pointer;">
          <td><strong style="color:var(--primary);">${e.mã_môn || '-'}</strong></td>
          <td><strong>${e.tên_môn || 'Môn học'}</strong></td>
          <td><span class="badge-role badge-student">${e.số_tín_chỉ} TC</span></td>
          <td><strong>${e.điểm_giữa_kỳ ?? 0}</strong></td>
          <td><strong>${e.điểm_cuối_kỳ ?? 0}</strong></td>
          <td><strong style="color:var(--primary);font-size:15px;">${e.điểm_tổng_kết ?? '-'}</strong></td>
          <td><span class="badge-role badge-teacher" style="font-weight:700;">${e.điểm_chữ}</span></td>
          <td>
            <div style="max-width: 220px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size:12.5px; color:var(--text-muted);" title="${e.nhận_xét || 'Không có nhận xét'}">
              ${e.nhận_xét || '<em>Chưa có nhận xét</em>'}
            </div>
          </td>
          <td>
            <button onclick="app.showGradeDetailModal('${e.định_danh}')" class="btn btn-secondary btn-sm" title="Xem chi tiết thẻ điểm">
              <i class="fa-solid fa-expand" style="color:var(--primary);"></i> Chi tiết
            </button>
          </td>
        </tr>
      `).join('');

      const gpaEl = document.getElementById('student-gpa-summary');
      if (gpaEl) {
        gpaEl.innerText = `GPA: ${tongKet.gpa_hệ_4 || '0.00'}/4.0 (Hệ 10: ${tongKet.gpa_hệ_10 || '0.00'}) - Tổng tín chỉ: ${tongKet.tổng_tín_chỉ || 0} - Xếp loại: ${tongKet.xếp_loại || '-'}`;
      }
    } catch (e) {}
  },

  async showGradeDetailModal(enrollmentId) {
    try {
      const res = await this.goiApi('/api/diem-so/bang-diem-cua-toi');
      const e = (res.kết_quả_học_tập || []).find(item => item.định_danh === enrollmentId);
      if (!e) return;

      const contentEl = document.getElementById('grade-detail-content');
      if (!contentEl) return;

      contentEl.innerHTML = `
        <div style="background: var(--bg-subtle); border: 1px solid var(--border-medium); border-radius: var(--radius-md); padding: 16px; margin-bottom: 16px;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; gap: 8px;">
            <h4 style="font-size: 17px; font-weight: 700; color: var(--text-main);">${e.tên_môn}</h4>
            <span class="badge-role badge-teacher" style="font-size: 12px; font-weight: 700;">${e.mã_môn}</span>
          </div>
          <div style="display: flex; gap: 16px; font-size: 12.5px; color: var(--text-muted); flex-wrap: wrap;">
            <span><i class="fa-solid fa-graduation-cap" style="color: var(--primary);"></i> Số tín chỉ: <strong>${e.số_tín_chỉ} Tín chỉ</strong></span>
            <span><i class="fa-solid fa-building-columns" style="color: var(--primary);"></i> Khoa: <strong>${e.khoa || 'Công nghệ thông tin'}</strong></span>
            <span><i class="fa-solid fa-calendar-days" style="color: var(--primary);"></i> Học kỳ: <strong>${e.học_kỳ || 'Học kỳ 1 - 2026'}</strong></span>
          </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 16px;">
          <div style="background: var(--bg-card); border: 1px solid var(--border-medium); border-radius: var(--radius-md); padding: 12px; text-align: center;">
            <div style="font-size: 11.5px; color: var(--text-dim); text-transform: uppercase; font-weight: 600;">Giữa kỳ (40%)</div>
            <div style="font-size: 20px; font-weight: 800; color: var(--text-main); margin-top: 4px;">${e.điểm_giữa_kỳ ?? 0}</div>
          </div>
          <div style="background: var(--bg-card); border: 1px solid var(--border-medium); border-radius: var(--radius-md); padding: 12px; text-align: center;">
            <div style="font-size: 11.5px; color: var(--text-dim); text-transform: uppercase; font-weight: 600;">Cuối kỳ (60%)</div>
            <div style="font-size: 20px; font-weight: 800; color: var(--text-main); margin-top: 4px;">${e.điểm_cuối_kỳ ?? 0}</div>
          </div>
          <div style="background: var(--primary-subtle); border: 1px solid var(--primary-border); border-radius: var(--radius-md); padding: 12px; text-align: center;">
            <div style="font-size: 11.5px; color: var(--primary); text-transform: uppercase; font-weight: 700;">Tổng Kết (Hệ 10)</div>
            <div style="font-size: 22px; font-weight: 800; color: var(--primary); margin-top: 2px;">${e.điểm_tổng_kết ?? '-'}</div>
          </div>
        </div>

        <div style="display: flex; gap: 10px; justify-content: space-between; align-items: center; background: var(--bg-subtle); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 12px 16px; margin-bottom: 16px; flex-wrap: wrap;">
          <div>
            <span style="font-size: 12.5px; color: var(--text-dim);">Điểm chữ:</span>
            <strong style="font-size: 16px; color: var(--primary); margin-left: 6px;">${e.điểm_chữ}</strong>
          </div>
          <div>
            <span style="font-size: 12.5px; color: var(--text-dim);">Quy đổi Hệ 4:</span>
            <strong style="font-size: 15px; color: var(--text-main); margin-left: 6px;">${e.điểm_hệ_4}/4.0</strong>
          </div>
          <div>
            <span style="font-size: 12.5px; color: var(--text-dim);">Học phí:</span>
            <span class="badge-role ${e.đã_đóng_học_phí ? 'badge-student' : 'badge-admin'}" style="margin-left: 6px;">${e.đã_đóng_học_phí ? 'Đã hoàn thành' : 'Chưa nộp'}</span>
          </div>
        </div>

        <div>
          <label style="display: block; font-size: 13px; font-weight: 700; color: var(--text-main); margin-bottom: 6px;">
            <i class="fa-solid fa-comment-dots" style="color: var(--primary); margin-right: 4px;"></i> Đánh Giá & Nhận Xét Của Giảng Viên:
          </label>
          <div style="background: var(--bg-card); border: 1px solid var(--border-medium); border-radius: var(--radius-md); padding: 14px 16px; font-size: 13.5px; line-height: 1.6; color: var(--text-main); min-height: 70px; max-height: 180px; overflow-y: auto; white-space: pre-wrap;">
            ${e.nhận_xét ? e.nhận_xét : '<em style="color:var(--text-dim);">Chưa có nhận xét chi tiết cho học phần này.</em>'}
          </div>
        </div>
      `;

      this.openModal('modal-grade-detail');
    } catch (e) {}
  },

  // -------------------------------------------------------------
  // 10. TRA CỨU HỌC PHÍ (SINH VIÊN)
  // -------------------------------------------------------------
  async loadTuitionView() {
    const tbody = document.getElementById('tuition-table-body');
    if (!tbody) return;

    try {
      const res = await this.goiApi('/api/hoc-phan/hoc-phi');
      const list = res.danh_sách || [];

      tbody.innerHTML = list.map(e => `
        <tr>
          <td><strong style="color:var(--primary);">${e.mã_môn}</strong></td>
          <td><strong>${e.tên_môn}</strong></td>
          <td>${e.số_tín_chỉ} Tín chỉ</td>
          <td>${e.đơn_giá_tín_chỉ.toLocaleString('vi-VN')} VNĐ</td>
          <td><strong style="color:#10b981;">${e.thành_tiền.toLocaleString('vi-VN')} VNĐ</strong></td>
          <td>
            ${e.đã_đóng_học_phí ? 
              '<span class="badge-role badge-student"><i class="fa-solid fa-circle-check"></i> Đã đóng</span>' : 
              '<span class="badge-role badge-admin"><i class="fa-solid fa-clock"></i> Chưa nộp</span>'
            }
          </td>
        </tr>
      `).join('');

      document.getElementById('tuition-total-credits').innerText = res.tổng_tín_chỉ || 0;
      document.getElementById('tuition-total-fee').innerText = (res.tổng_tiền || 0).toLocaleString('vi-VN') + ' VNĐ';

      const statusEl = document.getElementById('tuition-payment-status');
      if (statusEl) {
        if (list.length === 0) {
          statusEl.innerText = 'Chưa đăng ký môn';
          statusEl.style.color = 'var(--text-muted)';
        } else if (res.tất_cả_đã_đóng) {
          statusEl.innerText = '✅ Đã hoàn thành học phí';
          statusEl.style.color = '#10b981';
        } else {
          statusEl.innerText = '⏳ Chờ thanh toán';
          statusEl.style.color = '#f59e0b';
        }
      }
    } catch (e) {}
  },

  async payTuitionSimulation() {
    try {
      const ketQua = await this.goiApi('/api/hoc-phan/hoc-phi/thanh-toan', 'POST');
      this.toast('success', `🎉 ${ketQua.thông_báo}`);
      this.loadTuitionView();
    } catch (e) {}
  },

  // -------------------------------------------------------------
  // 11. QUẢN LÝ MÔN HỌC (ADMIN)
  // -------------------------------------------------------------
  async loadAdminCoursesView() {
    const tbody = document.getElementById('admin-courses-table-body');
    if (!tbody) return;

    try {
      const res = await this.goiApi('/api/mon-hoc');
      const list = res.danh_sách || [];

      tbody.innerHTML = list.map(c => `
        <tr>
          <td><strong style="color:var(--primary);">${c.mã_môn}</strong></td>
          <td><strong>${c.tên_môn}</strong></td>
          <td><span class="badge-role badge-student">${c.số_tín_chỉ} Tín chỉ</span></td>
          <td style="font-weight:600; color:var(--text-main);">${c.đơn_giá_tín_chỉ.toLocaleString('vi-VN')} đ</td>
          <td style="font-weight:700; color:#10b981;">${c.tổng_học_phí.toLocaleString('vi-VN')} đ</td>
          <td>${c.khoa || 'Công nghệ thông tin'}</td>
          <td>${c.học_kỳ || 'Học kỳ 1 - 2026'}</td>
          <td>
            <button onclick="app.deleteCourse('${c.định_danh}')" class="btn btn-danger btn-sm" title="Xóa môn học">
              <i class="fa-solid fa-trash"></i>
            </button>
          </td>
        </tr>
      `).join('');
    } catch (e) {}
  },

  showCreateCourseModal() {
    this.openModal('modal-create-course');
  },

  async handleCreateCourse(event) {
    event.preventDefault();
    const duLieu = {
      mã_môn: document.getElementById('c-code').value.trim(),
      tên_môn: document.getElementById('c-name').value.trim(),
      số_tín_chỉ: parseInt(document.getElementById('c-credits').value) || 3,
      đơn_giá_tín_chỉ: parseInt(document.getElementById('c-price-per-credit').value) || 450000,
      khoa: document.getElementById('c-dept').value.trim(),
      học_kỳ: document.getElementById('c-semester')?.value.trim() || 'Học kỳ 1 - 2026',
    };

    try {
      const ketQua = await this.goiApi('/api/mon-hoc', 'POST', duLieu);
      this.closeModal('modal-create-course');
      this.toast('success', ketQua.thông_báo);
      this.loadAdminCoursesView();
    } catch (e) {}
  },

  async deleteCourse(dinhDanh) {
    if (!confirm('Bạn có chắc chắn muốn xóa môn học này?')) return;
    try {
      const ketQua = await this.goiApi(`/api/mon-hoc/${dinhDanh}`, 'DELETE');
      this.toast('success', ketQua.thông_báo);
      this.loadAdminCoursesView();
    } catch (e) {}
  },

  // -------------------------------------------------------------
  // 12. TOÀN BỘ BẢNG ĐIỂM SINH VIÊN (TRANSCRIPT)
  // -------------------------------------------------------------
  async openStudentTranscript(studentId) {
    const container = document.getElementById('student-transcript-container');
    if (!container) return;

    try {
      const res = await this.goiApi(`/api/diem-so/bang-diem-sinh-vien/${studentId}`);
      const sv = res.sinh_viên;
      const courses = res.kết_quả_học_tập || [];
      const sum = res.tổng_kết || {};

      const courseRows = courses.map((en, index) => `
        <tr>
          <td style="text-align:center;font-weight:600;color:var(--text-dim);">${index + 1}</td>
          <td><strong style="color:var(--primary);">${en.mã_môn}</strong></td>
          <td>
            <strong>${en.tên_môn}</strong>
            <span style="display:block;font-size:11.5px;color:var(--text-dim);">${en.khoa || ''}</span>
          </td>
          <td style="text-align:center;"><span class="badge-role badge-student">${en.số_tín_chỉ} TC</span></td>
          <td style="text-align:center;font-weight:600;">${en.điểm_giữa_kỳ ?? '-'}</td>
          <td style="text-align:center;font-weight:600;">${en.điểm_cuối_kỳ ?? '-'}</td>
          <td style="text-align:center;">
            <strong style="font-size:14.5px;color:var(--primary);">${en.điểm_tổng_kết ?? '-'}</strong>
          </td>
          <td style="text-align:center;">
            <span class="badge-role badge-${en.mức === 'tốt' ? 'student' : (en.mức === 'khá' ? 'teacher' : 'admin')}">${en.điểm_chữ}</span>
          </td>
          <td style="text-align:center;font-weight:700;">${en.điểm_hệ_4}</td>
          <td style="text-align:center;">
            ${en.đã_đóng_học_phí ? 
              '<span class="badge-role badge-student"><i class="fa-solid fa-check"></i> Đã nộp</span>' : 
              '<span class="badge-role badge-admin"><i class="fa-solid fa-clock"></i> Chưa nộp</span>'
            }
          </td>
          <td style="font-size:12.5px;color:var(--text-muted);">${en.nhận_xét || 'Đạt yêu cầu học phần'}</td>
        </tr>
      `).join('');

      container.innerHTML = `
        <div style="background:var(--bg-subtle);border:1px solid var(--border-medium);border-radius:var(--radius-lg);padding:18px;margin-bottom:20px;">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;margin-bottom:18px;">
            <div style="display:flex;align-items:center;gap:14px;">
              <div class="user-avatar-sm" style="width:56px;height:56px;font-size:20px;flex-shrink:0;${sv.ảnh_đại_diện ? 'cursor:pointer;border:2px solid var(--primary);' : ''}" ${sv.ảnh_đại_diện ? `onclick="app.previewAvatar('${sv.định_danh}')" title="Xem ảnh"` : ''}>
                ${sv.ảnh_đại_diện ? `<img src="${sv.ảnh_đại_diện}" alt="${sv.họ_tên}">` : (sv.họ_tên || 'S').split(' ').pop().charAt(0)}
              </div>
              <div>
                <h3 style="font-size:18px;margin-bottom:4px;display:flex;align-items:center;gap:8px;">
                  ${sv.họ_tên}
                  <span class="badge-role badge-student" style="font-size:11px;">${sv.mã_số || 'SV-N/A'}</span>
                </h3>
                <div style="display:flex;align-items:center;gap:12px;font-size:12.5px;color:var(--text-muted);flex-wrap:wrap;">
                  <span><i class="fa-solid fa-building-columns" style="color:var(--primary);"></i> ${sv.khoa || 'Công nghệ thông tin'}</span>
                  <span><i class="fa-solid fa-graduation-cap"></i> ${sv.lớp || 'K66'}</span>
                  <span><i class="fa-solid fa-envelope"></i> ${sv.email || '-'}</span>
                </div>
              </div>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
              <span class="badge-role badge-${sum.mức === 'tốt' ? 'student' : (sum.mức === 'khá' ? 'teacher' : 'admin')}" style="font-size:13px;padding:6px 14px;font-weight:700;">
                <i class="fa-solid fa-medal"></i> Xếp loại: ${sum.xếp_loại || 'Khá'}
              </span>
            </div>
          </div>

          <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(160px, 1fr));gap:12px;">
            <div style="background:var(--bg-card);padding:12px 14px;border-radius:var(--radius-md);border:1px solid var(--border-subtle);text-align:center;">
              <span style="font-size:12px;color:var(--text-dim);display:block;">GPA Điểm Hệ 10</span>
              <strong style="font-size:22px;color:var(--primary);">${sum.gpa_hệ_10 || '0.00'}</strong>
              <span style="font-size:11px;color:var(--text-dim);display:block;">Thang điểm 10.0</span>
            </div>
            <div style="background:var(--bg-card);padding:12px 14px;border-radius:var(--radius-md);border:1px solid var(--border-subtle);text-align:center;">
              <span style="font-size:12px;color:var(--text-dim);display:block;">GPA Điểm Hệ 4</span>
              <strong style="font-size:22px;color:#10b981;">${sum.gpa_hệ_4 || '0.00'}</strong>
              <span style="font-size:11px;color:var(--text-dim);display:block;">Thang điểm 4.0</span>
            </div>
            <div style="background:var(--bg-card);padding:12px 14px;border-radius:var(--radius-md);border:1px solid var(--border-subtle);text-align:center;">
              <span style="font-size:12px;color:var(--text-dim);display:block;">Tín Chỉ Tích Lũy</span>
              <strong style="font-size:22px;color:var(--text-main);">${sum.tổng_tín_chỉ || 0}</strong>
              <span style="font-size:11px;color:var(--text-dim);display:block;">${courses.length} Môn học</span>
            </div>
            <div style="background:var(--bg-card);padding:12px 14px;border-radius:var(--radius-md);border:1px solid var(--border-subtle);text-align:center;">
              <span style="font-size:12px;color:var(--text-dim);display:block;">Học Phí Tích Lũy</span>
              <strong style="font-size:16px;color:#3b82f6;line-height:28px;">${(sum.học_phí_đã_đóng || 0).toLocaleString('vi-VN')} đ</strong>
              <span style="font-size:11px;color:${sum.đã_hoàn_thành_học_phí ? '#10b981' : '#ef4444'};display:block;">
                ${sum.đã_hoàn_thành_học_phí ? '✅ Đã hoàn thành' : '⚠️ Còn nợ học phí'}
              </span>
            </div>
          </div>
        </div>

        <div class="table-wrapper" style="border:1px solid var(--border-subtle);border-radius:var(--radius-md);overflow-x:auto;">
          <table class="data-table" style="margin:0;">
            <thead>
              <tr>
                <th style="width:40px;text-align:center;">STT</th>
                <th>Mã Môn</th>
                <th>Tên Môn Học</th>
                <th style="text-align:center;">Tín Chỉ</th>
                <th style="text-align:center;">Giữa Kỳ (40%)</th>
                <th style="text-align:center;">Cuối Kỳ (60%)</th>
                <th style="text-align:center;">Tổng Kết (10)</th>
                <th style="text-align:center;">Điểm Chữ</th>
                <th style="text-align:center;">Hệ 4</th>
                <th style="text-align:center;">Học Phí</th>
                <th>Đánh Giá & Nhận Xét</th>
              </tr>
            </thead>
            <tbody>
              ${courses.length > 0 ? courseRows : `
                <tr>
                  <td colspan="11" style="text-align:center;padding:30px;color:var(--text-dim);">
                    Sinh viên chưa đăng ký hoặc chưa có điểm học phần nào.
                  </td>
                </tr>
              `}
            </tbody>
          </table>
        </div>
      `;

      this.openModal('modal-student-transcript');
    } catch (e) {}
  },

  printStudentTranscript() {
    window.print();
  },

  // -------------------------------------------------------------
  // 13. XEM ẢNH ĐẠI DIỆN LIGHTBOX
  // -------------------------------------------------------------
  async previewAvatar(userId) {
    try {
      const res = await this.goiApi(`/api/ho-so/the-thong-tin/${userId}`);
      const user = res.thẻ;

      if (!user.ảnh_đại_diện) {
        this.toast('info', `Người dùng ${user.họ_tên} chưa tải lên ảnh đại diện.`);
        return;
      }

      const titleEl = document.getElementById('avatar-preview-title');
      const subtitleEl = document.getElementById('avatar-preview-subtitle');
      const imgEl = document.getElementById('avatar-preview-img');

      if (titleEl) titleEl.textContent = `Hồ Sơ Ảnh: ${user.họ_tên}`;
      if (subtitleEl) subtitleEl.textContent = `${user.mã_số ? user.mã_số + ' • ' : ''}${user.vai_trò} • ${user.khoa || user.lớp || 'Trường Đại Học'}`;
      if (imgEl) {
        imgEl.src = user.ảnh_đại_diện;
        imgEl.alt = user.họ_tên;
      }

      this.resetAvatarZoom();
      this.openModal('modal-avatar-preview');
    } catch (e) {}
  },

  zoomAvatar(delta) {
    this.phongToAnh = Math.min(Math.max(0.4, +(this.phongToAnh + delta).toFixed(2)), 4.0);
    this.applyAvatarTransform();
  },

  resetAvatarZoom() {
    this.phongToAnh = 1.0;
    this.gocXoayAnh = 0;
    this.applyAvatarTransform();
  },

  rotateAvatar(deg = 90) {
    this.gocXoayAnh = (this.gocXoayAnh + deg) % 360;
    this.applyAvatarTransform();
  },

  handleAvatarWheel(event) {
    if (event) {
      event.preventDefault();
      const delta = event.deltaY < 0 ? 0.2 : -0.2;
      this.zoomAvatar(delta);
    }
  },

  applyAvatarTransform() {
    const img = document.getElementById('avatar-preview-img');
    if (img) {
      img.style.transform = `scale(${this.phongToAnh}) rotate(${this.gocXoayAnh}deg)`;
    }
  },

  // -------------------------------------------------------------
  // 14. TIỆN ÍCH MODAL & FLOATING WIDGET
  // -------------------------------------------------------------
  toggleContactWidget() {
    const subMenu = document.getElementById('floating-sub-menu');
    if (subMenu) {
      subMenu.classList.toggle('open');
    }
  },

  openModal(modalId) {
    const m = document.getElementById(modalId);
    if (m) m.classList.add('show');
  },

  closeModal(modalId) {
    const m = document.getElementById(modalId);
    if (m) m.classList.remove('show');
  }
};

window.app = dieuKhien;

document.addEventListener('DOMContentLoaded', () => {
  app.init();
});
