import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# Initialize session state to store tasks
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# Function to add a new task
def add_task(game_name, company, start_date, end_date, status, notes):
    st.session_state.tasks.append({
        'Game Name': game_name,
        'Company': company,
        'Start': start_date,
        'Finish': end_date,
        'Status': status,
        'Notes': notes
    })

# Function to remove a task
def remove_task(task_index):
    if 0 <= task_index < len(st.session_state.tasks):
        st.session_state.tasks.pop(task_index)

# Function to update a task
def update_task(index, game_name, company, start_date, end_date, status, notes):
    if 0 <= index < len(st.session_state.tasks):
        st.session_state.tasks[index] = {
            'Game Name': game_name,
            'Company': company,
            'Start': start_date,
            'Finish': end_date,
            'Status': status,
            'Notes': notes
        }

# Function to load tasks from a CSV file
def load_tasks_from_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)
    for _, row in df.iterrows():
        add_task(row['Game Name'], row['Company'], pd.to_datetime(row['Start']), pd.to_datetime(row['Finish']), row['Status'], row['Notes'])

# Sidebar for adding new tasks
with st.sidebar:
    st.header("Add New Task")

    game_name = st.text_input("Game Name", key="add_game_name")
    company = st.text_input("Company", key="add_company")
    start_date = st.date_input("Start Date", min_value=datetime.now(), key="add_start_date")
    end_date = st.date_input("End Date", min_value=start_date, key="add_end_date")
    status = st.selectbox("Status", ["Not Started", "In Progress", "Completed", "Hold", "Delayed"], key="add_status")
    notes = st.text_area("Notes", key="add_notes")

    if st.button("Add Task", key="add_task_button"):
        add_task(game_name, company, start_date, end_date, status, notes)
        st.success("Task added successfully!")

# Sidebar for uploading tasks from a file
with st.sidebar:
    st.header("Upload Tasks from File")

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"], key="file_uploader")
    if uploaded_file is not None:
        load_tasks_from_csv(uploaded_file)
        st.success("Tasks loaded successfully!")

# Sidebar for choosing edit or delete
with st.sidebar:
    st.header("Manage Tasks")
    task_action = st.radio("Choose Action", ("None", "Edit Task", "Delete Task"), key="task_action")

    if task_action != "None" and st.session_state.tasks:
        task_names = [f"{task['Game Name']} - {task['Start']} to {task['Finish']}" for task in st.session_state.tasks]
        selected_task_index = st.selectbox("Select Task", range(len(task_names)), format_func=lambda x: task_names[x], key="select_task")
        
        if task_action == "Edit Task":
            st.write("Editing Task:", task_names[selected_task_index])
            
            edit_game_name = st.text_input("Game Name", value=st.session_state.tasks[selected_task_index]['Game Name'], key="edit_game_name")
            edit_company = st.text_input("Company", value=st.session_state.tasks[selected_task_index]['Company'], key="edit_company")
            edit_start_date = st.date_input("Start Date", value=st.session_state.tasks[selected_task_index]['Start'], key="edit_start_date")
            edit_end_date = st.date_input("End Date", value=st.session_state.tasks[selected_task_index]['Finish'], key="edit_end_date")
            edit_status = st.selectbox("Status", ["Not Started", "In Progress", "Completed", "Hold", "Delayed"], index=["Not Started", "In Progress", "Completed", "Hold", "Delayed"].index(st.session_state.tasks[selected_task_index]['Status']), key="edit_status")
            edit_notes = st.text_area("Notes", value=st.session_state.tasks[selected_task_index]['Notes'], key="edit_notes")

            if st.button("Update Task", key="update_task_button"):
                update_task(selected_task_index, edit_game_name, edit_company, edit_start_date, edit_end_date, edit_status, edit_notes)
                st.success("Task updated successfully!")

        elif task_action == "Delete Task":
            st.write("Deleting Task:", task_names[selected_task_index])
            if st.button("Delete Task", key="delete_task_button"):
                remove_task(selected_task_index)
                st.success("Task deleted successfully!")
                # Clear the selection
                selected_task_index = None
    elif not st.session_state.tasks:
        st.write("No tasks available to edit or delete.")

# Create DataFrame for the Gantt chart
if st.session_state.tasks:
    df = pd.DataFrame(st.session_state.tasks)
    df['Start'] = pd.to_datetime(df['Start'])
    df['Finish'] = pd.to_datetime(df['Finish'])

    # Custom color map for task statuses
    color_discrete_map = {
        "Not Started": "lightblue",
        "In Progress": "blue",
        "Completed": "green",
        "Hold": "tan",
        "Delayed": "red"
    }

    # Create Gantt chart with custom colors using plotly.graph_objects
    fig = go.Figure()

    for status, color in color_discrete_map.items():
        df_status = df[df['Status'] == status]
        fig.add_trace(go.Bar(
            x=df_status['Finish'] - df_status['Start'],
            y=df_status['Game Name'],
            base=df_status['Start'],
            orientation='h',
            name=status,
            marker=dict(color=color)
        ))

    fig.update_layout(
        title='Project timelines',
        xaxis_title='Time',
        yaxis_title='Game Name',
        barmode='stack',
        yaxis={'categoryorder':'total ascending'},
    )

    # Main container
    with st.container():
        st.header("Status tracker")

        # Display the Gantt chart
        st.plotly_chart(fig)
        
        # Convert DataFrame to CSV
        csv = df.to_csv(index=False)
        st.sidebar.download_button(
            label="Download CSV",
            data=csv,
            file_name='tasks.csv',
            mime='text/csv',
            key="download_csv_button"
        )
else:
    st.write("No tasks to display in the Gantt chart.")

# Bar chart of task statuses using plotly.graph_objects
if st.session_state.tasks:
    status_counts = df['Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']

    fig_bar = go.Figure()

    fig_bar.add_trace(go.Bar(
        x=status_counts['Status'],
        y=status_counts['Count'],
        marker=dict(color=[color_discrete_map[status] for status in status_counts['Status']])
    ))

    fig_bar.update_layout(
        title='Task Status Distribution',
        xaxis_title='Status',
        yaxis_title='Game Count'
    )

    st.plotly_chart(fig_bar)

st.write("save files, edit and load from sidebar ")
st.info("build dw 8-27-24")