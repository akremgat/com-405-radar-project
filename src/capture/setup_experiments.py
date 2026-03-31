import os
import argparse
from utils.radar import radar
from utils.read_com import list_files, find_com_port, update_com_port_in_file

current_dir = os.getcwd()

# ----------------------------------------------------------------------------------------- #
#                              Experiment definitions                                       #
# ----------------------------------------------------------------------------------------- #

EXPERIMENTS = {
    "exp1_sitting_still": "Attentive baseline - subject sits still, hands on desk",
    "exp2_writing":       "Attentive active - subject writes on paper or types on keyboard",
    "exp3_phone":         "Distracted - subject uses smartphone on desk or in hand",
    "exp4_head_nodding":  "Distracted - subject turns/nods head, looks around",
    "exp5_fidgeting":     "Distracted - subject taps fingers, clicks pen repetitively",
}

# ----------------------------------------------------------------------------------------- #
#                              Folder setup                                                 #
# ----------------------------------------------------------------------------------------- #

def setup_experiment_folders(base_path):
    """Creates a folder for each experiment under base_path/data/"""
    for exp_name, description in EXPERIMENTS.items():
        exp_folder = os.path.join(base_path, "data", exp_name)
        if not os.path.isdir(exp_folder):
            os.makedirs(exp_folder)
            print(f"[CREATED]  {exp_folder}")
        else:
            print(f"[EXISTS]   {exp_folder}")

        # write a small README inside each folder
        readme_path = os.path.join(exp_folder, "README.txt")
        if not os.path.isfile(readme_path):
            with open(readme_path, "w") as f:
                f.write(f"Experiment: {exp_name}\n")
                f.write(f"Description: {description}\n")
                f.write("Radar placement: Frontal desk level, ~0.75m height, ~0.6m distance\n")
                f.write("Minimum repetitions: 10 per class\n")

# ----------------------------------------------------------------------------------------- #
#                              Capture one experiment                                       #
# ----------------------------------------------------------------------------------------- #

def capture_experiment(exp_name, config, base_path):
    """Runs radar capture for a given experiment and saves to its folder."""

    if exp_name not in EXPERIMENTS:
        print(f"Unknown experiment '{exp_name}'. Available experiments:")
        for name in EXPERIMENTS:
            print(f"  - {name}")
        return

    exp_path = os.path.join(base_path, "data", exp_name)
    record_lua_script = os.path.join(base_path, "scripts", "1843_record.lua")
    config_lua_script = os.path.join(base_path, f"{config}.lua")

    # update COM port in all lua files
    lua_files = list_files(os.path.join(base_path, "scripts"))
    com_number = find_com_port("Application")
    for lua_script in lua_files:
        update_com_port_in_file(lua_script, com_number)

    radar1 = radar()

    if config:
        radar1.mmwave_config(config_lua_script)

    # check for existing data
    existing = [f for f in os.listdir(exp_path) if f.endswith(".bin")]
    rep_number = len(existing) + 1
    capture_name = f"{exp_name}_rep{rep_number:02d}"

    print(f"\nCapturing: {capture_name}")
    print(f"Description: {EXPERIMENTS[exp_name]}")
    print(f"Saving to: {exp_path}\n")

    radar1.mmwave_capture(capture_name, exp_path, record_lua_script)
    print(f"[DONE] Saved as {capture_name}_Raw_0.bin")

# ----------------------------------------------------------------------------------------- #
#                                        Main                                               #
# ----------------------------------------------------------------------------------------- #

def parse_args():
    parser = argparse.ArgumentParser(description="Setup and capture radar experiments.")
    parser.add_argument("--setup", action="store_true", help="Create all experiment folders.")
    parser.add_argument("--capture", type=str, default="", help="Name of experiment to capture (e.g. exp1_sitting_still).")
    parser.add_argument("--config", type=str, default="scripts/1843_config_lowres", help="Lua config script (without .lua).")
    parser.add_argument("--list", action="store_true", help="List all available experiments.")
    return parser.parse_args()


def main(args):
    if args.list:
        print("\nAvailable experiments:")
        for name, desc in EXPERIMENTS.items():
            print(f"  {name}: {desc}")
        return

    if args.setup:
        print("\nSetting up experiment folders...")
        setup_experiment_folders(current_dir)
        print("\nAll folders ready!")
        return

    if args.capture:
        capture_experiment(args.capture, args.config, current_dir)
        return

    print("Use --setup to create folders, --capture <exp_name> to record, or --list to see experiments.")


if __name__ == "__main__":
    args = parse_args()
    main(args)