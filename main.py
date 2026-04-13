from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.image import Image
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.toast import toast
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from reportlab.lib.pagesizes import A4
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from threading import Thread
from kivy.properties import StringProperty, ListProperty
from kivy.utils import platform  # pour détecter la plateforme
from kivy.factory import Factory
from kivy.metrics import dp
import datetime
import sqlite3
from passlib.hash import pbkdf2_sha256
from reportlab.pdfgen import canvas
from functools import partial
import os
import webbrowser
import urllib.parse

Window.size = (360, 640)

# ============================
# SCREENS
# ============================


class SplashScreen(Screen):
    pass


class RegisterScreen(Screen):
    pass

class HomeContent(Screen):
    pass



class LoginScreen(Screen):
    pass


class HomeScreen(Screen):
    pass


class SearchScreen(Screen):
    pass


class ReserveScreen(Screen):
    pass


class ReservationCard(MDCard):
    res_id = StringProperty("")
    car_name = StringProperty("")
    location = StringProperty("")
    time = StringProperty("")

    def __init__(self, res_id="", car_name="", location="", time="", **kwargs):
        super().__init__(**kwargs)
        self.res_id = res_id
        self.car_name = car_name
        self.location = location
        self.time = time

    def load_reservations(self):
        reservations = [
            {"res_id": 1, "car_name": "Toyota Prado", "location": "Pointe-Noire", "time": "2026-04-02 09:00"},
            {"res_id": 2, "car_name": "Nissan Patrol", "location": "Brazzaville", "time": "2026-04-03 14:00"},
        # ... autres réservations
        ]

        # Vider la zone de cartes avant de recharger
        self.ids.reservation_box.clear_widgets()

        for r in reservations:
            card = ReservationCard(
                res_id=str(r["res_id"]),
                car_name=r["car_name"],
                location=f"LIVRAISON : {r['location']}",
                time=f"Départ : {r['time']}"
            )
            # Ajouter la carte au layout
            card.update_widgets()

class ReservationsScreen(Screen):
    def on_enter(self):
        # Se déclenche quand on clique sur l'onglet "Réservations"
        self.load_reservations()

    def load_reservations(self):
        container = self.ids.container_scroll
        container.clear_widgets() # On vide la liste avant de recharger

        app = MDApp.get_running_app()
        if not app.current_user:
            return

        # Connexion à ta DB SQLite
        conn = sqlite3.connect("prodrive.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, vehicle, location, start_date FROM reservations WHERE username=?", (app.current_user,))
        rows = cursor.fetchall()
        conn.close()

        # Création des cartes dynamiquement
        for row in rows:
            res_id, vehicle, loc, date = row
            card = Factory.ReservationCard()
            # On injecte les données dans les propriétés définies dans le KV
            card.car_name = str(vehicle)
            card.location = f"LIVRAISON : {loc}"
            card.time = f"Départ : {date}"
            card.res_id = str(res_id)
            container.add_widget(card)


class CarDetailScreen(Screen):
    pass

# ============================
# PROFILE SCREEN (ULTRA-PRO)
# ============================


class ProfileScreen(Screen):

    def show_infos(self):
        app = MDApp.get_running_app()
        user_info = app.get_user_info()

        if user_info:
            username, email = user_info

            dialog = MDDialog(
                title="👤 Informations personnelles",
                text=f"Nom d'utilisateur : {username}\nEmail : {email}",
                buttons=[
                    MDFlatButton(
                        text="FERMER",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()
        else:
            toast("Utilisateur introuvable")

    def show_reservations(self):
        reservations = MDApp.get_running_app().get_user_reservations()

        if reservations:
            text = "\n".join([f"• {r[0]}" for r in reservations])
        else:
            text = "Aucune réservation"

            dialog = MDDialog(
                title="🚗 Mes réservations",
                text=text,
                buttons=[
                    MDFlatButton(
                        text="FERMER",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()

    def show_payments(self):
        payments = MDApp.get_running_app().get_payment_history()

        if payments:
            text = "\n".join([f"• {p[0]}" for p in payments])
        else:
            text = "Aucun paiement"

            dialog = MDDialog(
                title="💳 Historique des paiements",
                text=text,
                buttons=[
                    MDFlatButton(
                        text="FERMER",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()

    def change_password(self):
        app = MDApp.get_running_app()

        old_password = MDTextField(
            hint_text="Ancien mot de passe",
            password=True
        )

        new_password = MDTextField(
            hint_text="Nouveau mot de passe",
            password=True
        )

        content = MDBoxLayout(
            orientation="vertical",
            spacing=20,
            size_hint_y=None,
            height=200
        )

        content.add_widget(old_password)
        content.add_widget(new_password)

        dialog = MDDialog(
            title="🔐 Changer mot de passe",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="ANNULER",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="VALIDER",
                    on_release=lambda x: (
                        app.change_password(
                            old_password.text,
                            new_password.text
                        ),
                        dialog.dismiss()
                    )
                )
            ]
        )
        dialog.open()

    def delete_account(self):
        app = MDApp.get_running_app()

        dialog = MDDialog(
            title="⚠ Supprimer le compte",
            text="Cette action est irréversible.\nVoulez-vous continuer ?",
            buttons=[
                MDFlatButton(
                    text="ANNULER",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="SUPPRIMER",
                    md_bg_color=(1, 0, 0, 1),
                    on_release=lambda x: (
                        app.delete_account(),
                        dialog.dismiss()
                    )
                )
            ]
        )
        dialog.open()

    def logout(self):
        MDApp.get_running_app().logout()

        # ============================
        # MDCard cliquable
        # ============================


class RippleCard(MDCard):
    pass

# ============================
# MAIN APP
# ============================


class ProDriveApp(MDApp):
    current_user = None

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.create_database()
        return Builder.load_file("main.kv")
    
    # ============================
    # DATABASE
    # ============================

    def create_database(self):
        self.conn = sqlite3.connect("prodrive.db")
        self.cursor = self.conn.cursor()

        # Table users
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            password TEXT
        )
        """)

        # Table vehicles
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            image TEXT
        )
        """)

        # Table vehicle_details
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_details(
            vehicle_name TEXT PRIMARY KEY,
            transmission TEXT,
            fuel TEXT,
            seats INTEGER,
            gps INTEGER,
            clim INTEGER,
            bluetooth INTEGER
        )
        """)

        # Table reservations
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            vehicle TEXT,
            start_date TEXT,
            end_date TEXT,
            location TEXT,
            status TEXT
        )
        """)

        self.conn.commit()

        # Remplir vehicles si vide
        self.cursor.execute("SELECT COUNT(*) FROM vehicles")
        count = self.cursor.fetchone()[0]
        if count == 0:
            vehicles = [
                # Berlines
                ("TOYOTA YARIS", "Berlines", "images/TOYOTA_YARIS.png"),
                ("TOYOTA AVENSIS", "Berlines", "images/TOYOTA AVENSIS.png"),
                ("TOYOTA AVENSIS DIVA", "Berlines", "images/TOYOTA_AVENSIS_DIVA.png"),
                ("CHEVROLET CRUZE", "Berlines", "images/chevrolet cruze.jpeg"),
                ("KIA K7", "Berlines", "images/Kia k7.jpeg"),
                ("KIA K9", "Berlines", "images/Kia k9.jpeg"),
                ("MERCEDES E300", "Berlines", "images/mercedes e300.jpeg"),
                # 4x4
                ("TOYOTA RAV4 II", "4x4", "images/Toyota RAV4_2.jpg"),
                ("TOYOTA HILUX VIGO", "4x4", "images/hillux vigo.jpeg"),
                ("TOYOTA HILUX REVO", "4x4", "images/hillux revo 4x4.jpeg"),
                ("TOYOTA BJ ", "4x4", "images/toyota BJ.jpeg"),
                # SUV
                ("SUZUKI GRAND VITARA 2015", "SUV","images/Suzuki grand vitara 2010-20215.jpg"),
                ("SUZUKI GRAND VITARA 2024", "SUV", "images/SUZUKI GRAND VITARA 2024.png"),
                ("TOYOTA URBAN CRUISER", "SUV", "images/TOYOTA URBAINE CRUISER 2024.png"),
                ("TOYOTA STARLET", "SUV", "images/Starlet.png"),
                ("TOYOTA RAV4 IV", "SUV", "images/Toyota rav4 .jpeg"),
                ("TOYOTA RAV4 V", "SUV", "images/Rav4 V.jpeg"),
                ("JETOUR X70 Plus", "SUV", "images/jetour x 70plus .jpeg"),
                ("JETOUR Dashing", "SUV", "images/jetour dashing.jpeg"),
                ("JETOUR T2 ", "SUV", "images/Jetour t2.jpeg"),
                ("TOYOTA FORTUNER", "SUV", "images/toyota fortuner.jpeg"),
                ("TOYOTA PRADO TXL", "SUV", "images/prado txl.jpeg"),
                ("TOYOTA PRADO", "SUV", "images/Prado 2024.jpeg"),
                # SUS
                ("LEXUS RX 570 ", "SUS", "images/lexus rx 570.jpeg"),
                ("TOYOTA LC V8 2021", "SUS", "images/toyota lc.jpeg"),
                ("TOYOTA LC V8 2023", "SUS", "images/toyota lc 2023.jpeg"),
                ("TOYOTA HIACE VAN", "SUS", "images/VAN.jpeg"),
                ("TOYOTA COASTER", "SUS", "images/toyota-coaster.jpeg"),
            ]
            self.cursor.executemany(
                "INSERT INTO vehicles(name, category, image) VALUES(?,?,?)",
                vehicles
            )
            self.conn.commit()

        # ensure problematic rows are fixed even if DB already existed
        corrections = {
            "TOYOTA YARIS": "images/TOYOTA_YARIS.png",
            "TOYOTA AVENSIS": "images/TOYOTA AVENSIS.png",
            "TOYOTA AVENSIS DIVA": "images/TOYOTA_AVENSIS_DIVA.png",
            "SUZUKI GRAND VITARA 2024": "images/SUZUKI GRAND VITARA 2024.png",
            "TOYOTA URBAN CRUISER": "images/TOYOTA URBAINE CRUISER 2024.png",
        }
        for nm, pth in corrections.items():
            self.cursor.execute("UPDATE vehicles SET image=? WHERE name=?", (pth, nm))
        self.conn.commit()

        # Remplir vehicle_details
        details = [
            # Berlines
            ("TOYOTA YARIS", "Automatique", "Essence", 5, 1, 1, 1),
            ("TOYOTA AVENSIS", "Automatique", "Diesel", 5, 1, 1, 1),
            ("TOYOTA AVENSIS DIVA", "Automatique", "Essence", 5, 1, 1, 1),
            ("CHEVROLET CRUZE", "Manuelle", "Essence", 5, 1, 1, 1),
            ("KIA K7", "Automatique", "Essence", 5, 1, 1, 1),
            ("KIA K9", "Automatique", "Essence", 5, 1, 1, 1),
            ("MERCEDES E300", "Automatique", "Essence", 5, 1, 1, 1),
            # 4x4
            ("TOYOTA RAV4 II", "Automatique", "Essence", 5, 1, 1, 1),
            ("TOYOTA HILUX VIGO", "Manuelle", "Diesel", 5, 1, 1, 1),
            ("TOYOTA HILUX REVO", "Automatique", "Diesel", 5, 1, 1, 1),
            ("TOYOTA BJ", "Manuelle", "Diesel", 5, 1, 1, 1),
            # SUV
            ("SUZUKI GRAND VITARA 2015", "Automatique", "Essence", 5, 1, 1, 1),
            ("SUZUKI GRAND VITARA 2024", "Automatique", "Essence", 5, 1, 1, 1),
            ("TOYOTA URBAN CRUISER", "Automatique", "Essence", 5, 1, 1, 1),
            ("TOYOTA STARLET", "Manuelle", "Essence", 5, 1, 1, 1),
            ("TOYOTA RAV4 IV", "Automatique", "Essence", 5, 1, 1, 1),
            ("TOYOTA RAV4 V", "Automatique", "Essence", 5, 1, 1, 1),
            ("JETOUR X70 Plus", "Automatique", "Essence", 7, 1, 1, 1),
            ("JETOUR Dashing", "Automatique", "Essence", 5, 1, 1, 1),
            ("JETOUR T2", "Automatique", "Essence", 5, 1, 1, 1),
            ("TOYOTA FORTUNER", "Automatique", "Diesel", 7, 1, 1, 1),
            ("TOYOTA PRADO TXL", "Automatique", "Diesel", 7, 1, 1, 1),
            ("TOYOTA PRADO", "Automatique", "Diesel", 7, 1, 1, 1),
            # SUS
            ("LEXUS RX 570", "Automatique", "Essence", 5, 1, 1, 1),
            ("TOYOTA LC V8 2021", "Automatique", "Diesel", 7, 1, 1, 1),
            ("TOYOTA LC V8 2023", "Automatique", "Diesel", 7, 1, 1, 1),
            ("TOYOTA HIACE VAN", "Manuelle", "Diesel", 12, 0, 1, 0),
            ("TOYOTA COASTER", "Manuelle", "Diesel", 30, 0, 1, 0),
            # Ajouter les autres voitures de façon similaire
        ]
        self.cursor.executemany(
            "INSERT OR IGNORE INTO vehicle_details(vehicle_name, transmission, fuel, seats, gps, clim, bluetooth) VALUES(?,?,?,?,?,?,?)",
            details)
        self.conn.commit()
    # ============================
    # AUTHENTIFICATION
    # ============================

    def create_account(self, username, email, password):
        if not username or not email or not password:
            toast("Remplissez tous les champs")
            return

        hashed_password = pbkdf2_sha256.hash(password)

        try:
            self.cursor.execute(
                "INSERT INTO users(username,email,password) VALUES(?,?,?)",
                (username, email, hashed_password)
            )
            self.conn.commit()
            toast("Compte créé avec succès")
            self.root.current = "login"
        except sqlite3.IntegrityError:
            toast("Nom d'utilisateur déjà existant")

    def login(self, username, password):
        self.cursor.execute(
            "SELECT password FROM users WHERE username=?",
            (username,)
        )
        result = self.cursor.fetchone()

        if result:
            stored_password = result[0]
            if pbkdf2_sha256.verify(password, stored_password):
                self.current_user = username
                toast("Connexion réussie")
                self.root.current = "home"
                self.load_vehicles()
            else:
                toast("Mot de passe incorrect")
        else:
            toast("Utilisateur introuvable")

        # ============================
        # CAR DETAIL
        # ============================

    def show_car_details(self, vehicle_name, *args):
        try:
            # store the selection so the confirm button can use it
            self.selected_vehicle = vehicle_name

            # find the home screen and its inner manager
            home = self.root.get_screen("home")
            content = home.ids.content_manager

            # switch first so screen is instantiated and ids are populated
            content.current = "car_detail"
            screen = content.get_screen("car_detail")

            # récupérer l'image principale
            self.cursor.execute(
                "SELECT image FROM vehicles WHERE name=?",
                (vehicle_name,)
            )

            result = self.cursor.fetchone()
            if result:
                main_image = result[0]
            else:
                main_image = "images/defaut.jpg"

            # attempt to locate matching interior/rear images in the folder rather
            # than relying on a rigid naming convention.  We look for any file whose
            # name contains the vehicle name and the keyword 'interieur' or 'arriere'.
            interior_image = None
            rear_image = None
            dirname = os.path.dirname(main_image)
            # split the vehicle name into tokens so we match files containing any
            # part (e.g. 'TOYOTA YARIS' should match 'interieur yaris .jpg').
            tokens = [t.lower() for t in vehicle_name.split()]
            for fname in os.listdir(dirname):
                lower = fname.lower()
                if any(tok in lower for tok in tokens):
                    if "interieur" in lower or "interior" in lower:
                        interior_image = os.path.join(dirname, fname)
                    if "arri" in lower or "rear" in lower or "vue" in lower:
                        rear_image = os.path.join(dirname, fname)
            # fall back to default image if we didn't find any
            if not interior_image:
                interior_image = "images/defaut.jpg"
            if not rear_image:
                rear_image = "images/defaut.jpg"

            # set the initial image widget and remember alternatives
            print(f"[DEBUG] show_car_details: main={main_image}, interior={interior_image}, rear={rear_image}")
            screen.ids.detail_image.source = main_image
            screen.ids.detail_image.reload()
            screen.main_image = main_image
            screen.int_image = interior_image
            screen.rear_image = rear_image

            # récupérer et afficher les détails du véhicule
            self.cursor.execute(
                "SELECT transmission, fuel, seats, gps, clim, bluetooth FROM vehicle_details WHERE vehicle_name=?",
                (vehicle_name,)
            )
            details = self.cursor.fetchone()

            if details:
                transmission, fuel, seats, gps, clim, bluetooth = details
            else:
                transmission, fuel, seats, gps, clim, bluetooth = "N/A", "N/A", 0, 0, 0, 0

            screen.ids.transmission_label.text = transmission
            screen.ids.fuel_label.text = fuel
            screen.ids.seats_label.text = str(seats)
            screen.ids.gps_checkbox.active = bool(gps)
            screen.ids.clim_checkbox.active = bool(clim)
            screen.ids.bluetooth_checkbox.active = bool(bluetooth)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            print("Error in show_car_details:\n", tb)
            toast(f"Erreur: {e}")

    def set_detail_image(self, which):
        """Switch the main image of CarDetailScreen according to the tab.
        which is one of 'main', 'interior', 'rear'.
        """
        try:
            home = self.root.get_screen("home")
            content = home.ids.content_manager
            screen = content.get_screen("car_detail")
            # use the single detail_image widget and stored paths
            if which == "main":
                screen.ids.detail_image.source = screen.main_image
            elif which == "interior":
                screen.ids.detail_image.source = screen.int_image
            elif which == "rear":
                screen.ids.detail_image.source = screen.rear_image
            # force a reload so the widget updates immediately
            screen.ids.detail_image.reload()
        except Exception as e:
            print("Error switching detail image", e)

    def confirm_reservation(self):
        """Called from the detail screen when the user taps the confirm button.
        It simply re‑uses the old reservation dialog/procedure so you still get
        the payment confirmation pop‑up.  """
        if hasattr(self, 'selected_vehicle') and self.selected_vehicle:
            # reuse the existing flow that asks for payment confirmation
            self.reserve_vehicle(self.selected_vehicle)
        else:
            toast("Aucune voiture sélectionnée")

    # ============================
    # VEHICULES
    # ============================
    def load_vehicles(self, category=None, search_text=""):

        home = self.root.get_screen("home")
        search_screen = home.ids.content_manager.get_screen("search")
        vehicle_grid = search_screen.ids.vehicle_grid
        vehicle_grid.clear_widgets()

        # Construire la requête SQL
        query = "SELECT name, image FROM vehicles WHERE 1=1"
        params = []

        if category and category != "Tout":
            query += " AND category=?"
            params.append(category)

        if search_text:
            query += " AND name LIKE ?"
            params.append(f"%{search_text}%")

        # Exécuter la requête
        print(f"[DEBUG] load_vehicles query='{query}', params={params}")
        self.cursor.execute(query, params)
        results = self.cursor.fetchall()

        for name, image in results:
            # Vérifier l'existence de l'image
            if not os.path.exists(image):
                image = "images/defaut.jpg"

            # Création de la card (sans détails affichés dans la grille)
            bg_color = (1,1,1,1) if self.theme_cls.theme_style == "Light" else (0,0,0,1)
            card = RippleCard(
                orientation="vertical",
                size_hint=(0.45, None),
                height=280,
                padding=5,
                radius=[15],
                md_bg_color=bg_color,
                ripple_behavior=True
            )

            # Image principale
            img = Image(
                source=image,
                allow_stretch=True,
                keep_ratio=True,
                size_hint_y=0.5
            )
            card.add_widget(img)

            # Nom de la voiture
            label = MDLabel(
                text=name,
                halign="center",
                size_hint_y=0.1
            )
            card.add_widget(label)

            # Bouton "Réserver" (ouvre l'écran de détail)
            btn = MDRaisedButton(
                text="Réserver",
                size_hint_y=0.2,
                on_release=lambda x, n=name: self.show_car_details(n)
            )
            card.add_widget(btn)

            # Ajouter la card dans le grid
            vehicle_grid.add_widget(card)

        # ============================
        # FILTRAGE RECHERCHE
        # ============================

    def filter_vehicles(self, search_text):
        self.load_vehicles(category=None, search_text=search_text)

        # ============================
        # RESERVATION
        # ============================

    def reserve_vehicle(self, vehicle_name, *args):
        self.dialog = MDDialog(
            title="Paiement",
            text=f"Confirmer paiement pour {vehicle_name} ?",
            buttons=[
                MDFlatButton(
                    text="ANNULER",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="PAYER",
                    on_release=lambda x: self.confirm_payment(vehicle_name)
                ),
            ]
        )
        self.dialog.open()

    def confirm_payment(self, vehicle_name):
        self.dialog.dismiss()

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        self.cursor.execute(
            """INSERT INTO reservations(username, vehicle, start_date, location, status)
            VALUES(?,?,?,?,?)""",
            (self.current_user, vehicle_name, now, "Pointe-Noire", "Confirmée")
        )

        self.conn.commit()
        toast("Paiement réussi ✅")

        self.update_reservations_screen()

    # À mettre DANS la classe ProDriveApp
    def load_reservations(self):
        try:
            # Récupérer le layout qui contiendra les cartes de réservation
            reservations_layout = self.root.ids.reservations_layout  # Assure-toi que l'ID correspond

            # On vide le layout avant de rajouter les nouvelles cartes
            reservations_layout.clear_widgets()

            # Récupérer les réservations depuis la base de données
            self.cursor.execute("SELECT id, vehicle, location, time FROM reservations WHERE username=?", (self.current_user,))
            reservations = self.cursor.fetchall()
    
            if not reservations:
                from kivymd.toast import toast
                toast("Aucune réservation trouvée")
                return

                # Créer et ajouter chaque carte de réservation
            for res in reservations:
                res_id, vehicle, location, time = res
                card = ReservationCard(
                    res_id=res_id,
                    car_name=vehicle,
                    location=location,
                    time=time
                )
                reservations_layout.add_widget(card)

        except Exception as e:
            print("Erreur lors du chargement des réservations:", e)
    
    # ============================
    # FUNCTION UPDATE RESERVATIONS SCREEN
    # ============================
    def update_reservations_screen(self):
        try:
            home_screen = self.root.get_screen("home")
            res_screen = home_screen.ids.content_manager.get_screen("reservations")

            # On utilise l'ID du MDBoxLayout qui est dans ton ScrollView (id: container_scroll)
            container = res_screen.ids.container_scroll
            container.clear_widgets() # On vide tout pour rafraîchir proprement
        except Exception as e:
            print(f"Erreur d'accès à l'écran : {e}")
            return

        # 2. Récupérer TOUTES les réservations de l'utilisateur
        self.cursor.execute(
            "SELECT id, vehicle, start_date, location FROM reservations WHERE username=? ORDER BY id DESC",
            (self.current_user,)
        )
        reservations = self.cursor.fetchall()

        # 3. Mise à jour de la carte (MapView) en haut de l'écran si nécessaire
        user_lat = getattr(self, "user_lat", -4.7700)
        user_lon = getattr(self, "user_lon", 11.8500)
        if hasattr(res_screen, "mapview") and res_screen.mapview:
            res_screen.mapview.lat = user_lat
            res_screen.mapview.lon = user_lon
            res_screen.mapview.zoom = 15

            # 4. Créer une carte stylisée (ReservationCard) pour chaque ligne de la DB
            for res in reservations:
                res_id, vehicle, start_date, location = res

                # On crée l'objet à partir du modèle défini dans ton KV
                card = Factory.ReservationCard()

                # On injecte les données dans les propriétés de la carte
                card.res_id = str(res_id)
                card.car_name = str(vehicle)
                card.location = f"LIVRAISON : {location}"
                card.time = f"Départ : {start_date}"

                # On ajoute la carte à la liste défilante
                container.add_widget(card)

            if not reservations:
                container.add_widget(MDLabel(
                    text="Aucune réservation trouvée",
                    halign="center",
                    theme_text_color="Hint",
                    size_hint_y=None, height=dp(100)
                ))
                container.height=dp(100)
                    
    # ============================
    # FACTURE PDF
    # ============================
        
    def generate_invoice(self, vehicle_name):

        import datetime
        import random

        client_name = self.current_user
        reference = f"INV_PDV/2026/{random.randint(10000,99999)}"
        date_facturation = datetime.date.today().strftime("%d/%m/%Y")

        file_path = f"facture_{vehicle_name}.pdf"

        c = canvas.Canvas(file_path, pagesize=A4)

        # Logo
        if os.path.exists("logo 1.png"):
            c.drawImage("logo 1.png", 40, 730, width=150, height=80)
        
        # Titre facture
        c.setFont("Helvetica-Bold", 24)
        c.drawString(380, 750, "Facture")

        c.setFont("Helvetica", 11)
        c.drawString(380, 720, "#Référence de la facture :")
        c.drawString(380, 705, reference)

        # Infos entreprise
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, 680, "Pro Drive")

        c.setFont("Helvetica", 10)
        c.drawString(40, 660, "Location et Ventes des véhicules")
        c.drawString(40, 645, "RCCMP : CGPNR-04-2024-A10-00130")
        c.drawString(40, 630, "NIU : P240000000510072j")
        c.drawString(40, 615, "Régime d'imposition : Forfait")
        c.drawString(40, 600, "UTPPE : MPAKA")
        c.drawString(40, 585, "Mail : Contact.prodrive@gmail.com")
        c.drawString(40, 570, "Contact : 05 508 53 55 / 05 502 02 32")

        # Client
        c.drawString(380, 660, f"Client : {client_name}")
        c.drawString(380, 645, "Pointe-Noire, Congo")
        c.drawString(380, 630, "Tel : 06 123 456 78")
        c.drawString(380, 615, f"Date : {date_facturation}")

        # Tableau
        y = 520

        c.setFillColorRGB(0.1,0.3,0.6)
        c.rect(40, y, 520, 25, fill=True)

        c.setFillColorRGB(1,1,1)
        c.drawString(50, y+7, "DESCRIPTION")
        c.drawString(250, y+7, "PÉRIODE")
        c.drawString(340, y+7, "QTÉ")
        c.drawString(380, y+7, "PRIX UNIT.")
        c.drawString(470, y+7, "TOTAL HT")

        c.setFillColorRGB(0,0,0)

        y -= 30

        c.drawString(50, y, vehicle_name)
        c.drawString(250, y, "01/02/24 - 08/02/24")
        c.drawString(340, y, "1")
        c.drawString(380, y, "30 000 F")
        c.drawString(470, y, "30 000 F")

        y -= 25

        c.drawString(50, y, "Frais de nettoyage")
        c.drawString(340, y, "1")
        c.drawString(380, y, "5 000 F")
        c.drawString(470, y, "5 000 F")

        # Totaux
        c.drawString(380, 380, "Sous-total : 35 000")
        c.drawString(380, 365, "TVA (16%) : 5 600")

        c.setFillColorRGB(0.1,0.3,0.6)
        c.rect(360,340,200,25, fill=True)

        c.setFillColorRGB(1,1,1)
        c.drawString(370, 348, "TOTAL TTC : 40 600 FCFA")

        c.setFillColorRGB(0,0,0)

        c.drawString(40, 300, "Modes de paiement : Virement / Espèces")
        c.drawString(40, 280, "Merci de votre confiance")

        c.save()

        toast("Facture générée ✅")

    # ============================
    # ACTIONS RESERVATIONCARD
    # ============================
    def modify_reservation(self, res_id):
        # Exemple simple : juste un toast pour démonstration
        toast(f"Modifier réservation ID {res_id}")
        # Ici tu peux ouvrir un popup pour modifier la date, lieu, etc.

    def cancel_reservation(self, res_id):
        self.cursor.execute("DELETE FROM reservations WHERE id=? AND username=?", (res_id, self.current_user))
        self.conn.commit()
        toast(f"Réservation {res_id} annulée ✅")
        self.update_reservations_screen()

    def delete_reservation(self, res_id):
        # Même logique que cancel si tu veux supprimer complètement
        self.cancel_reservation(res_id)

    def invoice_reservation(self, res_id):
        self.cursor.execute("SELECT vehicle FROM reservations WHERE id=? AND username=?", (res_id, self.current_user))
        vehicle = self.cursor.fetchone()
        if vehicle:
            self.generate_invoice(vehicle[0])
        else:
            toast("Impossible de générer la facture")

        # ============================
        # PROFIL - INFOS / RESERVATIONS / PAIEMENTS / MOT DE PASSE / DELETE / LOGOUT
        # ============================

    def get_user_info(self):
        self.cursor.execute(
            "SELECT username, email FROM users WHERE username=?",
            (self.current_user,)
        )
        return self.cursor.fetchone()

    def get_user_reservations(self):
        self.cursor.execute(
            "SELECT vehicle FROM reservations WHERE username=?",
            (self.current_user,)
        )
        return self.cursor.fetchall()

    def get_payment_history(self):
        self.cursor.execute(
            "SELECT vehicle FROM reservations WHERE username=?",
            (self.current_user,)
        )
        return self.cursor.fetchall()

    def change_password(self, old_password, new_password):
        self.cursor.execute(
            "SELECT password FROM users WHERE username=?",
            (self.current_user,)
        )
        result = self.cursor.fetchone()

        if result:
            stored_password = result[0]

            if pbkdf2_sha256.verify(old_password, stored_password):
                new_hashed = pbkdf2_sha256.hash(new_password)

                self.cursor.execute(
                    "UPDATE users SET password=? WHERE username=?",
                    (new_hashed, self.current_user)
                )
                self.conn.commit()
                toast("Mot de passe modifié avec succès ✅")
            else:
                toast("Ancien mot de passe incorrect ❌")

    def delete_account(self):
        self.cursor.execute(
            "DELETE FROM users WHERE username=?",
            (self.current_user,)
        )

        self.cursor.execute(
            "DELETE FROM reservations WHERE username=?",
            (self.current_user,)
        )

        self.conn.commit()
        self.current_user = None
        toast("Compte supprimé")
        self.root.current = "login"

    def logout(self):
        self.current_user = None
        toast("Déconnecté")
        self.root.current = "login"

    # ============================
    # NAVIGATION
    # ============================

    def go_to_screen(self, screen_name):
        home = self.root.get_screen("home")
        home.ids.content_manager.current = screen_name
        if screen_name == "reservations":
            self.load_reservations()
            self.update_reservations_screen()

    def open_filters(self):
        toast("Filtres bientôt disponibles")

    def open_whatsapp(self):
        numero = "242055020232"  # mets ton vrai numéro WhatsApp ici

        message = "Bonjour, je souhaite obtenir des informations sur la location de voiture chez Pro Drive."
        message_encode = urllib.parse.quote(message)

        url = f"https://wa.me/{numero}?text={message_encode}"

        webbrowser.open(url)

    def toggle_theme(self):
        """Switch between light and dark mode and refresh vehicle grid.
        """
        if self.theme_cls.theme_style == "Light":
            self.theme_cls.theme_style = "Dark"
            toast("Mode sombre activé")
        else:
            self.theme_cls.theme_style = "Light"
            toast("Mode clair activé")
        # reload vehicles so their card backgrounds update to match theme
        self.load_vehicles()

if __name__ == "__main__":
    ProDriveApp().run()
    