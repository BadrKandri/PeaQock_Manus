from core.Yielding import log_agent_message
import os
from core.paths import (
    excel_path, context_path, profiler_notes_path, review_notes_path,
    repo_path, media_json_path, workspace_path, summary_path)

def run_preprocessing(manager):
    log_agent_message("Data extraction started")
    extractor = manager.get_data_extractor_agent()
    extractor.run()
    log_agent_message("✅ All Data extracted successfully")

    log_agent_message("Scouting the excel file...")
    scout = manager.get_scout_agent()
    scout_response = scout.run(f"Run the initial data scout on '{excel_path}' and save the report to '{context_path}'.")
    log_agent_message(f"✅ Scouting is finished.")

    log_agent_message("Understanding excel file...")
    profiler = manager.get_profiler_agent()
    profiler_response = profiler.run(f"Analyze the data in '{excel_path}' to understand its business context and save your findings to '{profiler_notes_path}'.")
    log_agent_message(f"✅ Understanding is finished.")

    log_agent_message("Analysing excel file...")
    analyst = manager.get_analyst_agent()
    analyst_response = analyst.run(f"Read the scout report from 'context.json' and the profiler notes from 'context_notes.txt'. Then, perform a deeper analysis on the file at {excel_path} and update the report at {context_path} with all findings.")
    log_agent_message("✅ Analysing has been completed.")

    log_agent_message("Reviewing the preprocessing analysis...")
    reviewer = manager.get_preprocessing_reviewer_agent()
    reviewer_response = reviewer.run(f"Review the JSON report at 'context.json' for logical errors and save your findings to '{review_notes_path}'.")
    log_agent_message("✅ Review Complete")

    log_agent_message("Correcting analysis...")
    if review_notes_path.exists() and review_notes_path.stat().st_size > 0:
        correction_response = analyst.run(f"A review of your previous work has been completed. The notes are in 'review_notes.txt'. Please read the notes and correct the JSON report at 'context.json' accordingly.")
        log_agent_message("✅ Full Inspection and Correction Completed")
    else:
        log_agent_message("❌ No review notes found or review notes were empty. The report is considered final.")

    workspace = manager.get_workspace_agent(context_note_path=profiler_notes_path, context_path=context_path, repo_path=repo_path, media_json_path=media_json_path)
    workspace.run()

    summary_exist = False
    while not summary_exist:
        summary_agent = manager.get_summary_agent(repo_path=repo_path, excel_path=excel_path, profiler_notes_path=profiler_notes_path, workspace_path=workspace_path)
        summary_response = summary_agent.run()
        if os.path.isfile(summary_path):
            summary_exist = True
            log_agent_message("✅ The Preprocessing is Done\n")
        log_agent_message("Creating summary...\n")

