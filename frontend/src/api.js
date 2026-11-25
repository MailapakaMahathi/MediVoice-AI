const API_BASE_URL = "http://127.0.0.1:8000";

export async function getDoctors() {
  const response = await fetch(`${API_BASE_URL}/doctors`);

  if (!response.ok) {
    throw new Error("Failed to fetch doctors");
  }

  return response.json();
}

export async function getAppointments() {
  const response = await fetch(`${API_BASE_URL}/appointments`);

  if (!response.ok) {
    throw new Error("Failed to fetch appointments");
  }

  return response.json();
}

export async function getAvailability(specialty = "") {
  const url = specialty
    ? `${API_BASE_URL}/availability?specialty=${encodeURIComponent(specialty)}`
    : `${API_BASE_URL}/availability`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error("Failed to fetch availability");
  }

  return response.json();
}