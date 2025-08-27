import sys, os, shutil, time, gc
from pathlib import Path
from dotenv import load_dotenv
from agents.agents import AgentManager
from core.Structured_Output import OrchestratorDecision
from core.Yielding import log_agent_message
from core.paths import excel_path, profiler_notes_path,repo_path, workspace_path, todo
from services.Preprocessing import run_preprocessing
from services.Run_Agents import run_agents

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = key
manager = AgentManager("gpt-4o")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main_flow(query: str):
    final_message = ""
    
    log_agent_message("⏱ Preprocessing ...")
    run_preprocessing(manager)

    log_agent_message("⏱ Planning steps ...")
    planner = manager.get_planner_agent(query=query, todo=todo).run()
    log_agent_message("✅The plan has been created succefully ,  You can follow the steps of my plan in the Task Progress section\n⏱ Running first step ...")
    orchestrator = manager.get_orchestrator_agent(todo=todo)
    
    while True:
        decision_response = orchestrator.run("Read the todo.md file and decide the next step.")
        
        if not isinstance(decision_response.content, OrchestratorDecision):
            log_agent_message(f"❌ failed to make a valid decision. Halting.\nReceived: {decision_response.content}")
            break
            
        decision = decision_response.content
        
        if decision.agent_to_call == 'complete':
            log_agent_message("✅ All tasks are complete. Workflow finished.")
            break
        else:
            agent_success = run_agents(query, manager, decision)
            if not agent_success:
                log_agent_message("❌ Agent execution failed.")

    log_agent_message("⏱ The output is being generated...")
    delivery_agent = manager.get_delivery_agent(query=query, repo_path=repo_path, excel_path=excel_path, profiler_notes_path=profiler_notes_path, workspace_path=workspace_path).run()
    output = delivery_agent.content.chosen_path
    clickable_link = getattr(delivery_agent.content, 'clickable_link', '')

    gc.collect()
    time.sleep(1)

    log_agent_message("⏱ one more second...")
    try:
        final = "output"; os.makedirs(final, exist_ok=True)
        shutil.copy(output, final) if os.path.isfile(output) else shutil.copytree(output, os.path.join(final, os.path.basename(output)), dirs_exist_ok=True)
        
        output_dir_path = Path(final)
        html_files = list(output_dir_path.glob('*.html'))
        
        if os.path.exists(repo_path): shutil.rmtree(repo_path)
    except FileNotFoundError as e:
        log_agent_message(f"❌ PeaQock Manus failed, File not found: {e}")
        final_message = f"❌ Error: File not found - {e}"
    except Exception as e:
        log_agent_message(f"❌ Error copying output: {e}")
        final_message = f"❌ Error copying output: {e}"
    
    return final_message if final_message else "✅ Task completed successfully!"