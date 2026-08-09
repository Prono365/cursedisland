from cursed_island.enemies import get_enemy_dialog_lines


def test_regular_enemy_dialog_is_returned():
    lines = get_enemy_dialog_lines("guard_novice", "encounter")
    assert lines
    assert any("Stop" in line or "Hey" in line for line in lines)


def test_boss_midfight_falls_back_to_phase_or_encounter_dialog():
    lines = get_enemy_dialog_lines("maxwell_enforcer", "mid_fight")
    assert lines
    assert any("Maxwell" in line or "ends here" in line.lower() or "deliver" in line.lower() for line in lines)
