"""
App launcher.

This script contains the main interface of the app.
"""
import pandas as pd
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField

from src.utils import opponent_datasheets
from src.workflow import launch_workflow
from src.dice import compute_average_enemy_dead, compute_average_hp_lost

from time import time


class Main(MDApp):

    # Value given to a text if it does not fill the conditions of parsing
    # (e.g.  value is not int > transformed into `ERROR_VALUE`)
    ERROR_VALUE = -1000

    # Width of the checkboxes
    CHECKBOX_TEXT_W = 150

    MINIMAL_HEIGHT = dp(10)

    # Set to True if you want to print info during the computation
    LAUNCH_WORKFLOW_VERBOSE = False

    def build(self):
        """
        Main function permitting to build kivy interface.
        """

        # Themes
        # --------------------------------------------------------------------------------------
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"

        # Main screen
        self.screen = ScrollView(size_hint=(1, None),  # scroll only for y
                                 size=(Window.width, Window.height),
                                 )

        # Grids permits to get thinks one by one
        self.grid = MDBoxLayout(orientation="vertical",
                                padding=dp(20),
                                spacing=self.MINIMAL_HEIGHT,  # spacing (top-bottom) between each elements of the grid
                                adaptive_height=True,
                                )

        # Make sure the height is such that there is something to scroll.
        self.grid.bind(minimum_height=self.grid.setter('height'))

        self.screen.add_widget(self.grid)

        # Main title
        self.grid.add_widget(MDLabel(text='40k Dice stats',
                                     font_style="H2",
                                     halign="center",
                                     size_hint_y=None,
                                     height=40,
                                     ))
        # Description
        self.grid.add_widget(MDLabel(text='This little app permits you to compute stats on typical enemy. \n'
                                          'Usage: just modify a value in a box, the results will automatically update.',
                                     size_hint_y=None,
                                     ))

        # Number of figs of the attacking unit
        self.field_nb_figs = MDTextField(id='nb_figs',
                                         text=str(10),
                                         hint_text='Nb figurines',
                                         size_hint_x=None,
                                         width=300,
                                         icon_right="account-multiple",
                                         size_hint_y=None,
                                         height=40,
                                         required=True,
                                         on_release=lambda x: self.compute()
                                         )
        self.grid.add_widget(self.field_nb_figs)

        # ------------------------------------------
        # Weapon characteristics
        # ------------------------------------------
        g1 = MDGridLayout(rows=1,
                          padding=dp(20),  # Left padding
                          size_hint_y=None, )

        # Nb attack
        self.field_a = MDTextField(id='A',
                                   text=str(1),
                                   hint_text='A',
                                   size_hint_x=None,
                                   width=100,
                                   icon_right="ammunition",
                                   required=True,
                                   on_text_validate=lambda x: self.compute()
                                   )
        g1.add_widget(self.field_a)

        # BS
        self.field_bs = MDTextField(id='bs',
                                    text="3+",
                                    hint_text='CT',
                                    size_hint_x=None,
                                    width=100,
                                    icon_right="adjust",
                                    required=True,
                                    on_release=lambda x: self.compute()
                                    )
        g1.add_widget(self.field_bs)

        # s
        self.field_s = MDTextField(id='S',
                                   hint_text='S',
                                   text=str(4),
                                   size_hint_x=None,
                                   width=100,
                                   icon_right="arm-flex",
                                   required=True,
                                   on_release=lambda x: self.compute()
                                   )
        g1.add_widget(self.field_s)

        # AP
        self.field_ap = MDTextField(id='AP',
                                    hint_text='AP',
                                    text=str(-1),
                                    size_hint_x=None,
                                    width=100,
                                    icon_right="shield-alert",
                                    required=True,
                                    on_release=lambda x: self.compute()
                                    )
        g1.add_widget(self.field_ap)

        # Damage
        self.field_dmg = MDTextField(id='D',
                                     text=str(1),
                                     hint_text='D',
                                     size_hint_x=None,
                                     width=100,
                                     icon_right="decagram",
                                     required=True,
                                     on_release=lambda x: self.compute()
                                     )
        g1.add_widget(self.field_dmg)

        # Critical
        self.field_crits = MDTextField(id='crit',
                                       text=str(6),
                                       hint_text='crit',
                                       size_hint_x=None,
                                       width=100,
                                       icon_right="creation",
                                       required=True,
                                       on_release=lambda x: self.compute()
                                       )
        g1.add_widget(self.field_crits)

        self.grid.add_widget(g1)

        # ------------------------------------------
        # Bonues (options)
        # ------------------------------------------
        # Main title
        self.grid.add_widget(MDLabel(text='Additionnal options',
                                     font_style="H5",
                                     halign="center",
                                     size_hint_y=None,
                                     height=40,
                                     ))
        # TODO: sous forme de menu déroulant:
        self.sustain_hit = MDTextField(id='sh',
                                       text=str(0),
                                       hint_text='Sustain (ex "D3+1")',
                                       size_hint_x=None,
                                       width=100,
                                       required=True,
                                       on_release=lambda x: self.compute()
                                       )
        self.grid.add_widget(self.sustain_hit)

        # ------------------------------------------
        # Checkobxes (options)
        # ------------------------------------------
        g2 = MDGridLayout(cols=6,
                          padding=dp(20),  # Left padding
                          size_hint_y=None,
                          # spacing=dp(20)
                          )

        self.grid.add_widget(g2)

        # Re-roll the 1 at the hit dice
        # ------------------------------------------
        g2.add_widget(MDLabel(size_hint_x=None,
                              width=self.CHECKBOX_TEXT_W,
                              text='Re-roll hit 1'))

        # Re-roll the 1 at the hit dice
        self.rr_hit_ones = MDCheckbox(id="rr_hit_ones",
                                      size_hint_x=None,
                                      width=50,
                                      on_release=lambda x: self._check_checkbox_rr_hit_ones_and_compute()
                                      )

        g2.add_widget(self.rr_hit_ones)

        # Re-roll the 1 at the wound dice
        # ------------------------------------------
        g2.add_widget(MDLabel(size_hint_x=None, width=self.CHECKBOX_TEXT_W, text='Re-roll wound 1'))
        self.rr_wounds_one = MDCheckbox(id="rr_wounds_one",
                                        size_hint_x=None,
                                        width=50,
                                        on_release=lambda x: self._check_checkbox_rr_one_wound_and_compute()
                                        )
        g2.add_widget(self.rr_wounds_one)

        # Lethal hit
        # ------------------------------------------
        g2.add_widget(MDLabel(size_hint_x=None, width=self.CHECKBOX_TEXT_W, text='Lethal hit'))
        self.field_lethal_hit = MDCheckbox(id="lethal_hit",
                                           size_hint_x=None,
                                           width=50,
                                           on_release=lambda x: self.compute()
                                           )
        g2.add_widget(self.field_lethal_hit)

        # Re-roll all the hit dice
        # ------------------------------------------
        g2.add_widget(MDLabel(size_hint_x=None, width=self.CHECKBOX_TEXT_W, text='Re-roll hit all'))

        # Re-roll the 1 at the hit dice
        self.rr_hit_all = MDCheckbox(id="rr_hit_all",
                                     size_hint_x=None,
                                     width=50,
                                     on_release=lambda x: self._check_checkbox_rr_hit_all_and_compute()
                                     )

        g2.add_widget(self.rr_hit_all)

        # Re-roll the all the wound dice
        # ------------------------------------------
        g2.add_widget(MDLabel(size_hint_x=None, width=self.CHECKBOX_TEXT_W, text='Twin'))
        self.rr_wound_all = MDCheckbox(id="rr_wound_all",
                                       size_hint_x=None,
                                       width=50,
                                       on_release=lambda x: self._check_checkbox_rr_all_wound_and_compute()
                                       )
        g2.add_widget(self.rr_wound_all)

        # Torrent
        # ------------------------------------------
        g2.add_widget(MDLabel(size_hint_x=None, width=self.CHECKBOX_TEXT_W, text='Torrent'))
        self.field_torrent = MDCheckbox(id="torrent",
                                        size_hint_x=None,
                                        width=50,
                                        on_release=lambda x: self.compute()
                                        )
        g2.add_widget(self.field_torrent)
        #
        # # Devastating wound
        # # ------------------------------------------
        g2.add_widget(MDLabel(size_hint_x=None, width=self.CHECKBOX_TEXT_W, text='Deva. wounds'))
        self.field_deva_wound = MDCheckbox(id="deva_wound",
                                           size_hint_x=None,
                                           width=50,
                                           on_release=lambda x: self.compute()
                                           )
        g2.add_widget(self.field_deva_wound)

        # ------------------------------------------
        # Submit button
        # ------------------------------------------
        self.submit_button = MDRectangleFlatButton(text='Submit')
        self.submit_button.bind(on_press=lambda x: self.compute())
        self.grid.add_widget(self.submit_button)

        # Space
        self.grid.add_widget(MDLabel(text=''))

        # ------------------------------------------
        # Results
        # ------------------------------------------
        # Init result df full of 0
        self.pandas_table = pd.DataFrame({"Name": opponent_datasheets["Name"],
                                          "average dead enemy": 0. * len(opponent_datasheets),
                                          "average HP lost": 0. * len(opponent_datasheets)})

        self.table = self.get_data_table(self.pandas_table)

        self.grid.add_widget(self.table)

        # Compute the first time
        self.compute()

        return self.screen

    def check_entry(self):
        """
        Check content of `field_nb_figs.text`. If not int > open error dialog box.
        """

        if self.parse_content(self.field_nb_figs.text) != self.ERROR_VALUE:
            print("OK")
        else:
            # Error popup
            self.dialog = MDDialog(title='Bad entry',
                                   text=f'Bad entry ("{self.field_nb_figs.text}"). Expected int !',
                                   size_hint=(0.8, 1),
                                   buttons=[MDFlatButton(text='Close', on_release=self.close_dialog)]
                                   )
            self.dialog.open()

    def compute(self):
        """
        Compute dice proba on all `opponent_datasheet`. Update `self.table`
        """
        start_process = time()

        print("COMPUTE")
        print("-"*200)
        # self.check_entry()

        # 1/ Retrieve results from user demand
        # ------------------------------------------
        nb_figs = int(self.field_nb_figs.text)
        crit = int(self.field_crits.text)
        weapon_a = int(self.field_a.text)

        if "+" in self.field_bs.text:
            # ex: 3+ into 3
            hit_threshold = int(self.field_bs.text.split("+")[0])
        else:
            hit_threshold = int(self.field_bs.text)
        weapon_s = int(self.field_s.text)
        # AP into positive number
        weapon_ap = -int(self.field_ap.text)
        weapon_d = int(self.field_dmg.text)

        sustain_hit = self.sustain_hit.text
        # TODO/ add field bonus wound
        bonus_wound = 0

        torrent = self.field_torrent.active
        rr_hit_ones = self.rr_hit_ones.active
        rr_hit_all = self.rr_hit_all.active
        lethal_hit = self.field_lethal_hit.active
        rr_wounds_ones = self.rr_wounds_one.active
        twin = self.rr_wound_all.active
        devastating_wounds = self.field_deva_wound.active

        # 2/ Compute
        # ------------------------------------------
        for name in opponent_datasheets["Name"]:
            # select one row
            current_carac = opponent_datasheets[opponent_datasheets["Name"] == name].iloc[0]
            # ex:
            # Name            marine
            # svg                  3
            # svg invul          7.0
            # feel no pain       7.0
            # toughness            4
            # w                    2

            # Compute the effect of the weapon on the current ennemy
            ennemy_dead, remaining_hp = launch_workflow(nb_figs=nb_figs,
                                                        crit=crit,
                                                        weapon_a=weapon_a,
                                                        hit_threshold=hit_threshold,
                                                        weapon_s=weapon_s,
                                                        weapon_ap=weapon_ap,
                                                        weapon_d=weapon_d,
                                                        sustain_hit=sustain_hit,
                                                        bonus_wound=bonus_wound,
                                                        torrent=torrent,
                                                        rr_hit_ones=rr_hit_ones,
                                                        rr_hit_all=rr_hit_all,
                                                        lethal_hit=lethal_hit,
                                                        rr_wounds_ones=rr_wounds_ones,
                                                        twin=twin,
                                                        devastating_wounds=devastating_wounds,
                                                        enemy_toughness=current_carac["toughness"],
                                                        svg_enemy=current_carac["svg"],
                                                        svg_invul_enemy=current_carac["svg invul"],
                                                        fnp_enemy=current_carac["feel no pain"],
                                                        ennemy_hp=current_carac["w"],
                                                        verbose=self.LAUNCH_WORKFLOW_VERBOSE)
            # Include `remaining_hp` in the average of deads
            average_ennemy_dead = compute_average_enemy_dead(enemy_dead=ennemy_dead, remaining_hp=remaining_hp, enemy_hp=current_carac["w"])
            average_hp_lost = compute_average_hp_lost(enemy_dead=ennemy_dead, remaining_hp=remaining_hp, enemy_hp=current_carac["w"])


            print(f"Average dead on {current_carac["Name"]}: {average_ennemy_dead}")

            # Fill result
            self.pandas_table.loc[
                self.pandas_table["Name"] == current_carac["Name"], "average dead enemy"] = average_ennemy_dead

            self.pandas_table.loc[
                self.pandas_table["Name"] == current_carac["Name"], "average HP lost"] = average_hp_lost

        self.update_data_table(self.pandas_table)

        print(f"Time to compute: {time() - start_process}s.")

    def close_dialog(self, obj):
        """
        Function to apply when clicking "close" on the dialog box -> close dialog box
        """
        self.dialog.dismiss()

    def parse_content(self, entry: str) -> int:
        """
        Parse content of `entry`.
        """
        try:
            entry_int = int(entry)
            return entry_int
        except:
            return self.ERROR_VALUE

    @staticmethod
    def get_data_table(dataframe: pd.DataFrame) -> MDDataTable:
        """
        Parse pandas `dataFrame` and return kivy `MDDataTable`
        """
        column_data = list(dataframe.columns)
        row_data = dataframe.to_records(index=False)

        column_data = [(x, dp(40)) for x in column_data]

        table = MDDataTable(
            column_data=column_data,
            row_data=row_data,
            use_pagination=False,
            height=dp(65 * len(dataframe)),
            size_hint_y=None,
            rows_num=len(dataframe),
        )
        return table

    def update_data_table(self, dataframe: pd.DataFrame) -> None:
        """
        Update `table.row_data` with `dataframe`content.
        """
        # Into correct format (list of tuples)
        df_formated = dataframe.to_records(index=False).tolist()

        self.table.row_data = df_formated

    # All checks > unselect incompatible checkbox when selecting new one
    # ------------------------------------------------
    def _check_checkbox_rr_hit_all_and_compute(self):
        """
        When selecting "reroll hit all" > unselect "reroll hit ones"
        Then, compute.
        """
        print("check_checkbox_rr_hit_all")
        if self.rr_hit_all.active:
            self.rr_hit_ones.active = False
        self.compute()

    def _check_checkbox_rr_hit_ones_and_compute(self):
        """
        When selecting "reroll hit ones" > unselect "reroll hit all"
        Then, compute.
        """
        print("check_checkbox_rr_hit_ones")
        if self.rr_hit_ones.active:
            self.rr_hit_all.active = False
        self.compute()
    def _check_checkbox_rr_one_wound_and_compute(self):
        """
        When selecting "rr_wounds_one" > unselect "rr_wound_all"
        Then, compute.
        """
        print("check_checkbox_rr_one_wound")
        if self.rr_wounds_one.active:
            self.rr_wound_all.active = False
        self.compute()
    def _check_checkbox_rr_all_wound_and_compute(self):
        """
        When selecting "rr_wound_all" > unselect "rr_wounds_one"
        Then, compute.
        """
        print("check_checkbox_rr_all_wound")
        if self.rr_wound_all.active:
            self.rr_wounds_one.active = False
        self.compute()


Main().run()
