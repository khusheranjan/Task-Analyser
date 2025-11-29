let tasks = [];

function addTask() {
    const t = {
        title: document.getElementById("title").value,
        due_date: document.getElementById("due_date").value || null,
        estimated_hours: Number(document.getElementById("hours").value),
        importance: Number(document.getElementById("importance").value),
        dependencies: document.getElementById("dependencies").value
            ? document.getElementById("dependencies").value.split(",").map(s => s.trim())
            : []
    };

    tasks.push(t);
    alert("Task added!");
}

async function analyze() {
    let finalTasks = tasks;

    // If user pasted JSON, override tasks
    const jsonText = document.getElementById("json_area").value;
    if (jsonText.trim().length > 0) {
        try {
            finalTasks = JSON.parse(jsonText);
        } catch (e) {
            alert("Invalid JSON");
            return;
        }
    }

    const res = await fetch("http://localhost:8000/api/tasks/analyze/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(finalTasks)
    });

    const data = await res.json();

    document.getElementById("results").textContent = JSON.stringify(data, null, 2);
}
