import streamlit as st
import pandas as pd
# import rumus as r # <-- BARIS INI DIKOMENTARI/DIHAPUS, JANGAN IMPORT DI AWAL
import datetime

st.set_page_config(page_title="Analisis Banyak Klaim", layout="wide")
st.title("Estimasi Banyak Klaim")
st.subheader("Pemodelan Waktu Antar Kedatangan (Distribusi Pareto)")

# --- Pastikan data ada ---
if 'uploaded_data' not in st.session_state or st.session_state.get('uploaded_data') is None:
    st.warning("Silakan unggah file CSV terlebih dahulu di halaman utama.")
    st.stop()

data = st.session_state['uploaded_data']
data["tanggal_klaim_diajukan"] = pd.to_datetime(
    data["tanggal_klaim_diajukan"], errors="coerce"
)

# --- Sidebar Rentang Tanggal ---
min_date = data["tanggal_klaim_diajukan"].min().date()
default_dates = st.session_state.get("analysis_dates", (min_date, datetime.date.today()))

tanggal = st.date_input(
    "Masukkan tanggal yang akan dianalisis:",
    value=default_dates,
    min_value=min_date,
    key="date_input"
)

if not (isinstance(tanggal, (list, tuple)) and len(tanggal) == 2):
    st.warning("Silakan pilih rentang tanggal yang lengkap (dua tanggal).")
    st.stop()
if tanggal == (min_date, datetime.date.today()):
    st.info("Default tanggal masih dari data ter-upload. Silakan ubah rentang tanggal untuk melanjutkan.")
    st.stop()

st.session_state.analysis_dates = tanggal
start_date, end_date = tanggal

# --- Navigasi antar tipe rumah sakit ---
if 'tipe_list' not in st.session_state:
    st.session_state.tipe_list = sorted(data['tipe_klasifikasi'].unique())
if 'idx_banyak' not in st.session_state:
    st.session_state.idx_banyak = 0

tipe_list = st.session_state.tipe_list
idx_banyak = st.session_state.idx_banyak
last = len(tipe_list) - 1

if idx_banyak < 0:
    st.session_state.idx_banyak = 0
    st.switch_page("pages/01_Analisis Deskriptif.py")
elif idx_banyak > last:
    st.session_state.idx_banyak = last
    st.session_state.idx_besar = 0
    st.switch_page("pages/03_Analisis Besar Klaim.py")

selected_tipe = tipe_list[idx_banyak]
st.sidebar.markdown(f"### Analisis Banyak Klaim — {selected_tipe}")

# --- Tombol untuk memicu analisis ---
if st.button(f"Jalankan Analisis Banyak Klaim untuk {selected_tipe}"):
    import rumus as r # <-- IMPORT DIPINDAHKAN KE DALAM TOMBOL
    
    with st.spinner("Sedang menjalankan analisis, mohon tunggu..."):
        # --- Jalankan analisis Pareto saja ---
        all_results = r.analisis_banyak_klaim(
            data, selected_tipe=selected_tipe,
            analysis_start=start_date, analysis_end=end_date
        )

        # --- Tampilkan hasil ---
        if selected_tipe in all_results:
            result = all_results[selected_tipe][0]

            st.subheader(f"Ringkasan Hasil Estimasi Parameter Distribusi Pareto dari Waktu Antar Kedatangan untuk {selected_tipe}")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Histogram**")
                st.image(result.get("Histogram"), use_container_width=True)
            with col2:
                st.markdown("**Fungsi Hazard**")
                st.image(result.get("Fungsi Hazard"), use_container_width=True)

            rentang_tanggal_str = f"{start_date.strftime('%Y/%m/%d')} - {end_date.strftime('%Y/%m/%d')}"

            df_summary = pd.DataFrame([{
                'Analisis': 'Banyak Klaim',
                'Rentang Tanggal Analisis': rentang_tanggal_str,
                'Parameter Proses Poisson': result.get('Fungsi Intensitas'),
                'Ekspektasi Banyak Klaim': result.get('Ekspektasi'),
                'Standar Deviasi Banyak Klaim': result.get('Standar Deviasi')
            }])
            
            with st.expander("Detail untuk Distribusi Pareto"):
                st.write(f"**Parameter:** {result.get('Parameter')}")
                st.write(f"**Kolmogorov Smirnov:** {result.get('Kolmogorov-Smirnov'):.4f}")
                st.write(f"**Critical Value:** {result.get('Critical Value'):.4f}")
                st.write(f"**H0 Ditolak:** {result.get('H0 Ditolak')}")

            st.subheader(f"Ringkasan Hasil Estimasi Banyak Klaim untuk {selected_tipe}")
            st.table(df_summary.style.format({
                'Parameter Proses Poisson': '{:,.4f}',
                'Ekspektasi Banyak Klaim': '{:,.4f}',
                'Standar Deviasi Banyak Klaim': '{:,.4f}'
            }))

            if 'tabel1' not in st.session_state or not isinstance(st.session_state.tabel1, dict):
                st.session_state.tabel1 = {}
            st.session_state.tabel1[selected_tipe] = df_summary

        else:
            st.warning(f"Analisis untuk '{selected_tipe}' tidak dapat diselesaikan atau tidak menghasilkan data.")
        
        st.success("Analisis selesai!")

# --- Tombol navigasi (tidak perlu diubah) ---
st.markdown("---")
def go_back():
    st.session_state.idx_banyak -= 1

def go_next():
    st.session_state.idx_banyak += 1

col1, col2, col3 = st.columns([1, 1, 8]) # Memberi ruang agar tidak terlalu lebar
with col1:
    st.button("Back", on_click=go_back, key="back_banyak", use_container_width=True)
with col2:
    st.button("Next", on_click=go_next, key="next_banyak", use_container_width=True)

st.stop()