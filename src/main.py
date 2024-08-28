"""
App launcher.

This script contains the main interface of the app.

Note that for performances issues, we are not yet using pandas to manipulate tables (`opponent_datasheet`).
It raise a more complex code but optimal.
"""
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
from time import time
from os.path import dirname, abspath
from sys import path

# Get the directory of the current file
current_dir = dirname(abspath(__file__))
# <absolute_path>/40k-dice-stats-computing/src/

# Get the parent directory
# parent_dir = dirname(current_dir)
# <absolute_path>/40k-dice-stats-computing/

# Add the parent directory to the Python path
path.insert(0, current_dir)

from common.enemy import opponent_datasheets
from common.workflow import launch_workflow
from common.dice import compute_average_enemy_dead, compute_average_hp_lost, DiceExpression, _parse_str_expression

class Main(MDApp):

    # Value given to a text if it does not fill the conditions of parsing
    # (e.g.  value is not int > transformed into `ERROR_VALUE`)
    ERROR_VALUE = -1000

    # Width of the checkboxes
    CHECKBOX_TEXT_W = Window.width / 4

    # Set to True if you want to print info during the computation
    LAUNCH_WORKFLOW_VERBOSE = False

    # Set to True if you want to test app on a screen of 6.4'' (representative of a smartphone)
    TEST = False
    if TEST:
        Window.size = (640, 1024)  # Set the window size to match the simulated screen

    # Width of one column of the table
    TABLE_COL_W = Window.width / 20

    # Spacing between each widget
    SPACING = Window.height / 20

    def build(self):
        """
        Main function permitting to build kivy interface.
        """

        # Themes
        # --------------------------------------------------------------------------------------
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"

        # Main screen
        self.screen = ScrollView(
                                size_hint = (1, 1), # full size screen
                                # size_hint=(1, None),  # scroll only for y
                                 size=(Window.width, Window.height),
                                 )

        # Grids permits to get thinks one by one
        self.grid = MDBoxLayout(orientation="vertical",
                                padding=dp(20),  # Set left padding to 0 to avoid black space
                                spacing=self.SPACING,  # Adjust space between each child component
                                adaptive_height=True,
                                size_hint_y=None,  # Box exceed Window heigh > permits the scroll
                                )

        # Make sure the height is such that there is something to scroll.
        self.grid.bind(minimum_height=self.grid.setter('height'))

        self.screen.add_widget(self.grid)

        # Main title
        self.grid.add_widget(MDLabel(text='40k Dice stats',
                                     font_style="H4",
                                     halign="center",
                                     size_hint_y=None,
                                     height=dp(20),  # top padding avoiding reduce text
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
                                         width=Window.width/3,
                                         icon_right="account-multiple",
                                         size_hint_y=None,
                                         # height=dp(20),
                                         required=True,
                                         on_release=lambda x: self.compute()
                                         )
        self.grid.add_widget(self.field_nb_figs)

        # ------------------------------------------
        # Weapon characteristics
        # ------------------------------------------
        g1 = MDGridLayout(rows=2,
                          size_hint_y=None,
                          height=2 * Window.height / 10  # pre-define height to avoid overlap
                        )
        # Nb attack
        self.field_a = MDTextField(id='A',
                                   text=str(1),
                                   hint_text='A',
                                   size_hint_x=None,
                                   width=Window.width/4,
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
                                    width=Window.width/4,
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
                                   width=Window.width/4,
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
                                    width=Window.width/4,
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
                                     width=Window.width/4,
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
                                       width=Window.width/4,
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
                                     # height=dp(30),
                                     ))
        # TODO: sous forme de menu déroulant:
        self.sustain_hit = MDTextField(id='sh',
                                       text=str(0),
                                       hint_text='Sustain (ex "D3+1")',
                                       size_hint_x=None,
                                       width=Window.width/3,
                                       required=True,
                                       on_text_validate=lambda x: self.compute()
                                       )
        self.grid.add_widget(self.sustain_hit)

        # ------------------------------------------
        # Checkobxes (options)
        # ------------------------------------------
        g2 = MDGridLayout(cols=2,
                          size_hint_y=None,
                          spacing=self.SPACING,  # force vertical spacing between each elements
                          height=8 * Window.height / 10  # pre-define height to avoid overlap
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
                                      width=Window.width/2,
                                      on_release=lambda x: self._check_checkbox_rr_hit_ones_and_compute()
                                      )

        g2.add_widget(self.rr_hit_ones)

        # Re-roll the 1 at the wound dice
        # ------------------------------------------
        g2.add_widget(MDLabel(size_hint_x=None, width=self.CHECKBOX_TEXT_W, text='Re-roll wound 1'))
        self.rr_wounds_one = MDCheckbox(id="rr_wounds_one",
                                        size_hint_x=None,
                                        width=Window.width/2,
                                        on_release=lambda x: self._check_checkbox_rr_one_wound_and_compute()
                                        )
        g2.add_widget(self.rr_wounds_one)

        # Lethal hit
        # ------------------------------------------
        g2.add_widget(MDLabel(size_hint_x=None, width=self.CHECKBOX_TEXT_W, text='Lethal hit'))
        self.field_lethal_hit = MDCheckbox(id="lethal_hit",
                                           size_hint_x=None,
                                           width=Window.width/2,
                                           on_release=lambda x: self.compute()
                                           )
        g2.add_widget(self.field_lethal_hit)

        # Re-roll all the hit dice
        # ------------------------------------------
        g2.add_widget(MDLabel(size_hint_x=None, width=self.CHECKBOX_TEXT_W, text='Re-roll hit all'))

        # Re-roll the 1 at the hit dice
        self.rr_hit_all = MDCheckbox(id="rr_hit_all",
                                     size_hint_x=None,
                                     width=Window.width/2,
                                     on_release=lambda x: self._check_checkbox_rr_hit_all_and_compute()
                                     )

        g2.add_widget(self.rr_hit_all)

        # Re-roll the all the wound dice
        # ------------------------------------------
        g2.add_widget(MDLabel(size_hint_x=None, width=self.CHECKBOX_TEXT_W, text='Twin'))
        self.rr_wound_all = MDCheckbox(id="rr_wound_all",
                                       size_hint_x=None,
                                       width=Window.width/2,
                                       on_release=lambda x: self._check_checkbox_rr_all_wound_and_compute()
                                       )
        g2.add_widget(self.rr_wound_all)

        # Torrent
        # ------------------------------------------
        g2.add_widget(MDLabel(size_hint_x=None, width=self.CHECKBOX_TEXT_W, text='Torrent'))
        self.field_torrent = MDCheckbox(id="torrent",
                                        size_hint_x=None,
                                        width=Window.width/2,
                                        on_release=lambda x: self.compute()
                                        )
        g2.add_widget(self.field_torrent)
        #
        # # Devastating wound
        # # ------------------------------------------
        g2.add_widget(MDLabel(size_hint_x=None, width=self.CHECKBOX_TEXT_W, text='Deva. wounds'))
        self.field_deva_wound = MDCheckbox(id="deva_wound",
                                           size_hint_x=None,
                                           width=Window.width/2,
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
        self.enemy_names = list(opponent_datasheets.keys())
        # ["marine", "sororita", ...]

        # Init result df full of 0
        self.result_dict = {"Name": self.enemy_names,
                            "average dead enemy": [0.] * len(self.enemy_names),  # [0, 0, ...]
                            "average HP lost": [0.] * len(self.enemy_names)}  # [0, 0, ...]

        self.widget_table = self.init_data_table(result_dict=self.result_dict)

        # Create a BoxLayout with left and right padding
        layout = MDBoxLayout(size_hint_y=None,
                             adaptive_height=True,
                             # padding=(self.TABLE_COL_W, Window.width/12, self.TABLE_COL_W, 0),  # (left, top, right, bottom)
                             padding=(Window.width / 15, Window.height / 24, Window.width / 15, 0),
                             )

        self.grid.add_widget(layout)

        layout.add_widget(self.widget_table)

        # Compute the first time
        self.compute()

        return self.screen

    # CHECKER
    # ----------------------------------------------------------------------------
    def check_entry_sustain_hit(self):
        """
        Check content of `self.sustain_hit.text`. If wrong format, open error dialog.
        Ex of correct format: "2D6+1", "2D6", "2".
        """
        if self.parse_str_to_dice_expression(self.sustain_hit.text)!= self.ERROR_VALUE:
            print("Content 'Sustain hit', value ok")
        else:
            # Error popup
            self.dialog = MDDialog(title='Bad entry',
                                   text=f'Bad entry "sustain hit". Expected format "XDY+Z" (ex: 2 or 2D6 or 3D6+4) !',
                                   size_hint=(0.8, 1),
                                   buttons=[MDFlatButton(text='Close', on_release=self.close_dialog)]
                                   )
            self.dialog.open()

    def check_int_entry(self, text_field_widget: MDTextField) -> None:
        """
        Check content of `field_text`. If not int > open error dialog box.

        :param text_field_widget: TextField widget to check
        :param format_expected: Format expected for `test_widget.text` (only used for message). Ex: "2D6+1". Ex: "int"
        """

        if self.parse_str_to_int(text_field_widget.text) != self.ERROR_VALUE:
            print(f"Content: '{text_field_widget.hint_text}', value ok")
        else:
            # Error popup
            self.dialog = MDDialog(title='Bad entry',
                                   text=f'Bad entry ("{text_field_widget.hint_text}"). Expected int !',
                                   size_hint=(0.8, 1),
                                   buttons=[MDFlatButton(text='Close', on_release=self.close_dialog)]
                                   )
            self.dialog.open()

    def close_dialog(self, obj):
        """
        Function to apply when clicking "close" on the dialog box -> close dialog box
        """
        self.dialog.dismiss()

    def parse_str_to_int(self, entry: str) -> int:
        """
        Parse content of `entry` (str -> int).
        """
        try:
            entry_int = int(entry)
            return entry_int
        except:
            return self.ERROR_VALUE

    def parse_str_to_dice_expression(self, entry: str) -> DiceExpression | int:
        """
        Parse content of `entry` (str -> DiceExpression).
        """
        try:
            entry_dice_expression = _parse_str_expression(entry)
            return entry_dice_expression
        except:
            return self.ERROR_VALUE

    # COMPUTE
    # ----------------------------------------------------------------------------
    def compute(self):
        """
        Compute dice proba on all `opponent_datasheet`. Update `self.result_dict`
        """
        start_process = time()

        print("COMPUTE")
        print("-"*200)

        # 0/ Check content of fields (if wrong content, app crash)
        # ------------------------------------------
        self.check_int_entry(self.field_nb_figs)
        self.check_int_entry(self.field_a)
        # DO NOT check CT as int entry, because contains "+" --> from now, not checked
        self.check_int_entry(self.field_s)
        self.check_int_entry(self.field_ap)
        self.check_int_entry(self.field_dmg)
        self.check_int_entry(self.field_crits)

        self.check_entry_sustain_hit()

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
        enemy_names = list(opponent_datasheets.keys())
        # ["marine", "sororita", ...]

        for index, name in enumerate(enemy_names):
            # select one row
            current_carac = opponent_datasheets[name]
            # ex: {'svg': 3, 'svg invul': None, 'feel no pain': None, 'toughness': 4, 'w': 2}

            # Compute the effect of the weapon on the current enemy
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

            print(f"Average dead on {name}: {average_ennemy_dead}")

            # Fill `result_dict`
            # ------------------------------------------
            self.result_dict['average dead enemy'][index] = average_ennemy_dead
            self.result_dict['average HP lost'][index] = average_hp_lost

        self.update_widget_table(self.result_dict)

        print(f"Time to compute: {time() - start_process}s.")

    # Manage table
    # ------------------------------------------------
    @staticmethod
    def __table_to_tuples(table: dict) -> list:
        """
        Transform `result_dict` (nested dict) into list of tuples
        Example:
        input: {'Name': ['marine', 'sororita',...], 'average dead enemy': [0.0, 0.0,..], 'average HP lost': [0.0, 0.0..]
        output: [('marine', 0.0, 0.0),  ('sororita', 0.0, 0.0),...]
        """
        return [(table["Name"][k],
                 table['average dead enemy'][k],
                 table["average HP lost"][k])
                for k in range(len(table["Name"]))]

    def init_data_table(self, result_dict: dict) -> MDDataTable:
        """
        Init a data result_dict with 0
        """
        column_data = list(result_dict.keys())
        # ['Name', 'average dead enemy', 'average HP lost']

        column_data = [(x, self.TABLE_COL_W ) for x in column_data]

        widget_table = MDDataTable(
            column_data=column_data,
            row_data=self.__table_to_tuples(result_dict),  # ex of line: ("marine", 0, 0)
            use_pagination=False,
            height= dp(65) * (Window.height / 10) * len(self.enemy_names),
            size_hint_y=None,
            rows_num=len(self.enemy_names),  # 1 line per enemy
        )

        return widget_table

    def update_widget_table(self, updated_dict: dict) -> None:
        """
        Update `widget_table.row_data` with `updated_dict`content.
        """
        # Into correct format (list of tuples)
        self.widget_table.row_data = self.__table_to_tuples(updated_dict)

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
