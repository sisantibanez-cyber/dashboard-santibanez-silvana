import streamlit as st
import pandas as pd
import plotly.express as px

# ================= CONFIGURACIÓN: cambia SOLO esta parte =================
ARCHIVO     = 'datos_limpios.csv'
TITULO      = 'Casas usadas en venta en la Región Metropolitana'
DESCRIPCION = 'Avisos de casas usadas en venta en la Región Metropolitana (chilepropiedades.cl, marzo de 2023): precio, comuna, metros construidos, dormitorios y baños. Datos limpios de la Actividad 2.2.'
AUTOR       = 'Silvana Santibáñez'
KAGGLE      = 'https://www.kaggle.com/datasets/luisfelipetn/valor-casas-usadas-chile-rm-08032023'

COL_CAT  = 'Comuna'            # columna de categorías
COL_NUM  = 'Precio_millones'   # columna numérica principal (millones de pesos)
COL_NUM2 = 'Built Area'        # segunda columna numérica (metros construidos)
# =========================================================================

st.set_page_config(page_title=TITULO, page_icon='📊', layout='wide')

@st.cache_data
def cargar_datos():
    return pd.read_csv(ARCHIVO)

df = cargar_datos()

st.title(f'📊 {TITULO}')
st.write(DESCRIPCION)

# ---------- BARRA LATERAL: filtros e información ----------
st.sidebar.header('Filtros')

categorias = sorted(df[COL_CAT].dropna().astype(str).unique())
sel_cat = st.sidebar.multiselect(f'{COL_CAT} (vacío = todas)', categorias)

minimo = float(df[COL_NUM].min())
maximo = float(df[COL_NUM].max())
rango = st.sidebar.slider(COL_NUM, minimo, maximo, (minimo, maximo))

st.sidebar.markdown('---')
st.sidebar.markdown(f'**Autor:** {AUTOR}  \n**Datos:** [Kaggle]({KAGGLE})')

df_f = df[df[COL_NUM].between(rango[0], rango[1])]
if sel_cat:
    df_f = df_f[df_f[COL_CAT].astype(str).isin(sel_cat)]

if df_f.empty:
    st.warning('No hay datos con estos filtros. Cambia la selección.')
    st.stop()

# ---------- INDICADORES (KPI) ----------
k1, k2, k3, k4 = st.columns(4)
k1.metric('Registros', f'{len(df_f):,}',
          delta=f'{len(df_f) / len(df) * 100:.1f}% del total',
          delta_color='off')
k2.metric(f'Promedio de {COL_NUM}', f'{df_f[COL_NUM].mean():,.2f}',
          delta=f'{df_f[COL_NUM].mean() - df[COL_NUM].mean():+,.2f} vs. total')
k3.metric(f'Mediana de {COL_NUM}', f'{df_f[COL_NUM].median():,.2f}')
k4.metric('Categoría más frecuente', str(df_f[COL_CAT].mode()[0]))

# ---------- GRÁFICOS ----------
top10 = df_f[COL_CAT].value_counts().head(10).index
df_top = df_f[df_f[COL_CAT].isin(top10)]

izq, der = st.columns(2)

conteo = df_top[COL_CAT].value_counts().reset_index()
conteo.columns = [COL_CAT, 'cantidad']
fig1 = px.bar(conteo, x='cantidad', y=COL_CAT, orientation='h',
              title=f'Registros por {COL_CAT} (10 más frecuentes)',
              labels={'cantidad': 'Cantidad de registros'})
fig1.update_layout(yaxis={'categoryorder': 'total ascending'})
izq.plotly_chart(fig1)

fig2 = px.histogram(df_f, x=COL_NUM, nbins=30,
                    title=f'Distribución de {COL_NUM}')
fig2.update_layout(yaxis_title='Cantidad de registros')
der.plotly_chart(fig2)

izq2, der2 = st.columns(2)

fig3 = px.box(df_top, x=COL_CAT, y=COL_NUM,
              title=f'{COL_NUM} según {COL_CAT}')
izq2.plotly_chart(fig3)

muestra = df_f.sample(min(len(df_f), 3000), random_state=1)
r = df_f[COL_NUM].corr(df_f[COL_NUM2])
fig4 = px.scatter(muestra, x=COL_NUM2, y=COL_NUM, opacity=0.5,
                  title=f'Relación entre {COL_NUM2} y {COL_NUM} (r = {r:.2f})')
der2.plotly_chart(fig4)

# ---------- DESAFÍO: treemap ----------
fig5 = px.treemap(conteo, path=[px.Constant('Total'), COL_CAT],
                  values='cantidad',
                  title=f'Proporción de registros por {COL_CAT}')
fig5.update_traces(textinfo='label+percent root')
st.plotly_chart(fig5)

# ---------- TABLA Y DESCARGA ----------
with st.expander('Ver los datos filtrados'):
    st.dataframe(df_f)
st.download_button('⬇ Descargar datos filtrados (CSV)',
                   data=df_f.to_csv(index=False).encode('utf-8'),
                   file_name='datos_filtrados.csv', mime='text/csv')

# ---------- CONCLUSIONES ----------
st.subheader('Conclusiones')
st.markdown('''
- **Hallazgo 1:** El valor típico de una casa es de 205,7 millones de pesos (mediana), mientras que el promedio es de 365,5 millones. Son distintos porque unas pocas casas muy caras suben el promedio.
- **Hallazgo 2:** Al filtrar por comuna, el precio cambia mucho: en La Pintana la mediana es de unos 68 millones de pesos y en Lo Barnechea de unos 991 millones.
- **Hallazgo 3:** La relación entre Built Area y el precio es moderada, con una correlación de r = 0,41: a más metros construidos el precio tiende a ser mayor, aunque la comuna también influye mucho.
''')
