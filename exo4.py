from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, Slider, Range1d, Select, CustomJS, HoverTool
from bokeh.layouts import column, row

# Fonctions pour calculer les termes de la suite
def eau_sale_dabord(vo, k, nmax, V=2500):
    """Calcule les termes de la suite pour le comportement 'Eau sale d'abord'."""
    v = [vo]
    clean = [vo]
    for i in range(1, nmax):
        v.append(min(min(k * v[-1], V), V - clean[-1]))
        clean.append(clean[-1] + v[-1])
    return v, clean

def eau_propre_dabord(vo, k, nmax, V=2500):
    """Calcule les termes de la suite pour le comportement 'Eau propre d'abord'."""
    v = [vo]
    clean = [vo]
    for i in range(1, nmax):
        v.append(max(min(k * v[-1], V) - clean[-1], 0))
        clean.append(clean[-1] + v[-1])
    return v, clean

def brassage(vo, k, nmax, V=2500):
    """Calcule les termes de la suite pour le comportement 'Brassage'."""
    v = [vo]
    clean = [vo]
    for i in range(1, nmax):
        v.append(min(k * v[-1], V) * (V - clean[-1]) / V)
        clean.append(clean[-1] + v[-1])
    return v, clean

def brassage_et_evaporation(vo, k, nmax, w, V=2500):
    """Calcule les termes de la suite pour le comportement 'Brassage et évaporation'."""
    v = [vo]
    clean = [vo * (1 - w / V)]
    for i in range(1, nmax):
        v.append(min(k * v[-1], V) * (V - clean[-1]) / V)
        clean.append((clean[-1] + v[-1]) * (1 - w / V))
    return v, clean

# Initialisation de la figure
p = figure(title="Nombre de bactérie au jour T", x_axis_label="t", y_axis_label="v",
           width=800, height=400, y_range=Range1d(0, 2500), x_range=Range1d(0, 10))

# Création des données source
data_v_bacteries = ColumnDataSource(data=dict(t=[], v=[]))

points_v_bacteries = p.circle(x='t', y='v', source=data_v_bacteries, size=8, color='blue', legend_label="Volume de bactéries le matin du jour t")

# Création des données source
data_v_eau_propre = ColumnDataSource(data=dict(t=[], v=[]))

points_v_eau_propre = p.circle(x='t', y='v', source=data_v_eau_propre, size=8, color='red', legend_label="Volume d'eau propre l'après midi du jour t")

# Fonction de mise à jour des données en réponse aux changements de sliders
def update(attr, old, new):
    # Récupération des valeurs des sliders
    V0 = vo_slider.value
    K = k_slider.value
    NMAX = nmax_slider.value
    selected_function = function_selector.value
    
    # Mise à jour de la variable w si nécessaire
    if selected_function == "Brassage et évaporation":
        W = w_slider.value
    
    # Calcul de la suite avec les nouvelles valeurs
    T_values = list(range(NMAX))
    
    if selected_function == "Eau sale d'abord":
        suite, clean = eau_sale_dabord(V0, K, NMAX)
    elif selected_function == "Eau propre d'abord":
        suite, clean = eau_propre_dabord(V0, K, NMAX)
    elif selected_function == "Brassage":
        suite, clean = brassage(V0, K, NMAX)
    elif selected_function == "Brassage et évaporation":
        suite, clean = brassage_et_evaporation(V0, K, NMAX, W)
    
    # Mise à jour des données source
    data_v_bacteries.data = dict(t=T_values, v=suite, color=["Bleu"]*NMAX)
    data_v_eau_propre.data = dict(t=T_values, v=clean, color=["Rouge"]*NMAX)

    p.x_range.end = NMAX

# Création des sliders pour modifier les paramètres
vo_slider = Slider(title="Volume initial (V0)", value=100, start=0, end=2500.0, step=0.1)
k_slider = Slider(title="Taux de reproduction (K)", value=1, start=0, end=10.0, step=0.01)
nmax_slider = Slider(title="Nombre maximal de termes", value=10, start=1, end=1000.0, step=1)
w_slider = Slider(title="Volume évaporé (W)", value=0, start=0, end=2500.0, step=0.1)
w_slider.visible = False

# Sélecteur pour choisir le comportement des bactéries
function_selector = Select(title="Comportement des bactéries", value="Eau sale d'abord",
                           options=["Eau sale d'abord", "Eau propre d'abord", "Brassage", "Brassage et évaporation"])

# Callback pour afficher ou masquer le slider w
w_visible = CustomJS(args=dict(slider=w_slider), code="""
    if (cb_obj.value == 'Brassage et évaporation') {
        slider.visible = true;
    } else {
        slider.visible = false;
    }
""")
function_selector.js_on_change('value', w_visible)

# Liaison des sliders à la fonction de mise à jour
for slider in [vo_slider, k_slider, nmax_slider, w_slider, function_selector]:
    slider.on_change('value', update)

hover = HoverTool()
hover.tooltips = [("Jour", "@t"), ("Volume", "@v{0,0.000}"), ("Série", "@color")]

# Spécifiez les renderers à considérer lors du survol.
hover.renderers = [points_v_bacteries, points_v_eau_propre]

p.add_tools(hover)

# Mise en page des éléments
layout = column(row(function_selector, w_slider), vo_slider, k_slider, nmax_slider, p)

# Ajout de la mise en page à l'application
curdoc().add_root(layout)

update(None, None, None)