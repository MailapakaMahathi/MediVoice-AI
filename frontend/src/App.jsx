import { PipecatClient } from "@pipecat-ai/client-js";
import { WebSocketTransport } from "@pipecat-ai/websocket-transport";
import { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Activity,
  ArrowUpRight,
  CalendarDays,
  Clock,
  HeartPulse,
  LayoutDashboard,
  Phone,
  ShieldCheck,
  Stethoscope,
  Users,
  X,
  CheckCircle2,
  Menu,
} from "lucide-react";

import { getDoctors, getAppointments } from "./api";

function App() {
  // -----------------------------
  // STATE
  // -----------------------------
  const [doctors, setDoctors] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [loadingDoctors, setLoadingDoctors] = useState(true);
  const [loadingAppointments, setLoadingAppointments] = useState(true);
  const [doctorError, setDoctorError] = useState("");
  const [appointmentError, setAppointmentError] = useState("");

  const [isCallOpen, setIsCallOpen] = useState(false);
  const [callSeconds, setCallSeconds] = useState(0);
  const [connectionStatus, setConnectionStatus] = useState("disconnected");
  const websocketRef = useRef(null);
  const audioStreamRef = useRef(null);

  // -----------------------------
  // FETCH DOCTORS
  // -----------------------------
  useEffect(() => {
    getDoctors()
      .then((data) => {
        setDoctors(data);
        setDoctorError("");
      })
      .catch((error) => {
        setDoctorError(error.message || "Failed to load doctors.");
      })
      .finally(() => {
        setLoadingDoctors(false);
      });
  }, []);

  // -----------------------------
  // FETCH APPOINTMENTS
  // -----------------------------
  const loadAppointments = () => {
  setLoadingAppointments(true);

  getAppointments()
    .then((data) => {
      setAppointments(data);
      setAppointmentError("");
    })
    .catch((error) => {
      setAppointmentError(
        error.message || "Failed to load appointments."
      );
    })
    .finally(() => {
      setLoadingAppointments(false);
    });
};

  useEffect(() => {
  getAppointments()
    .then((data) => {
      setAppointments(data);
      setAppointmentError("");
    })
    .catch((error) => {
      setAppointmentError(
        error.message || "Failed to load appointments."
      );
    })
    .finally(() => {
      setLoadingAppointments(false);
    });
}, []);

  // -----------------------------
  // CALL TIMER
  // -----------------------------
  useEffect(() => {
    if (!isCallOpen) return;

    const interval = setInterval(() => {
      setCallSeconds((previous) => previous + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [isCallOpen]);

  const formattedTime = `${String(
  Math.floor(callSeconds / 60)
).padStart(2, "0")}:${String(callSeconds % 60).padStart(2, "0")}`;

const startCall = async () => {
  setCallSeconds(0);
  setIsCallOpen(true);
  setConnectionStatus("connecting");

  try {
    const transport = new WebSocketTransport();

    const client = new PipecatClient({
      transport,
      enableMic: true,
      callbacks: {
        onConnected: () => {
          console.log("MediVoice AI connected 🎙️");
          setConnectionStatus("connected");
        },
        onDisconnected: () => {
          console.log("MediVoice AI disconnected");
          setConnectionStatus("disconnected");
        },
        onError: (error) => {
          console.error("Pipecat error:", error);
          setConnectionStatus("error");
        },
      },
    });

    websocketRef.current = client;

    await client.connect({
      ws_url: "ws://127.0.0.1:8000/ws/voice",
    });
  } catch (error) {
    console.error("Voice connection error:", error);
    setConnectionStatus("error");
  }
};

const endCall = async () => {
  try {
    if (websocketRef.current) {
      await websocketRef.current.disconnect();
      websocketRef.current = null;
    }

    if (audioStreamRef.current) {
      audioStreamRef.current.getTracks().forEach((track) => track.stop());
      audioStreamRef.current = null;
    }
  } catch (error) {
    console.error("Error ending call:", error);
  }

  setIsCallOpen(false);
  setConnectionStatus("disconnected");
};

  // -----------------------------
  // NAVIGATION
  // -----------------------------
  const scrollToSection = (sectionId) => {
    document.getElementById(sectionId)?.scrollIntoView({
      behavior: "smooth",
    });
  };

  // -----------------------------
  // MAIN DASHBOARD
  // -----------------------------
  return (
    <div className="app-container">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <HeartPulse size={22} />
          </div>
          <div className="brand-text">
            <h2>MediVoice</h2>
            <span>AI HEALTHCARE</span>
          </div>
        </div>

        <div className="sidebar-label">MENU</div>

        <nav className="sidebar-nav">
          <button
            className="nav-item active"
            onClick={() => scrollToSection("overview")}
          >
            <LayoutDashboard size={18} />
            <span>Overview</span>
          </button>

          <button
            className="nav-item"
            onClick={() => scrollToSection("doctors")}
          >
            <Stethoscope size={18} />
            <span>Doctors</span>
          </button>

          <button
            className="nav-item"
            onClick={() => scrollToSection("appointments")}
          >
            <CalendarDays size={18} />
            <span>Appointments</span>
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-support-card">
            <div className="support-icon">
              <ShieldCheck size={20} />
            </div>
            <h4>Your health matters</h4>
            <p>We're here to make healthcare simpler and accessible.</p>
            <button onClick={startCall}>
              Talk to MediVoice <ArrowUpRight size={15} />
            </button>
          </div>

          <div className="sidebar-footer">
            <div className="sidebar-footer-icon">
              <HeartPulse size={17} />
            </div>
            <span>MediVoice AI</span>
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="main-content">
        {/* TOP BAR */}
        <header className="topbar">
          <div className="topbar-left">
            <button className="mobile-menu-button">
              <Menu size={20} />
            </button>
            <div>
              <span className="breadcrumb">Workspace / </span>
              <strong>Overview</strong>
            </div>
          </div>

          <div className="topbar-right">
            <div className="system-status">
              <span className="status-dot" />
              System operational
            </div>
          </div>
        </header>

        {/* OVERVIEW */}
        <section className="dashboard-content" id="overview">
          <div className="welcome-section">
            <div>
              <div className="section-eyebrow">YOUR HEALTHCARE ASSISTANT</div>
              <h1>Healthcare, made <span>simpler.</span></h1>
              <p>
                Connect with doctors and manage appointments with
                your voice-powered healthcare assistant.
              </p>
            </div>
          </div>

          {/* HERO CARD */}
          <motion.section
            className="hero-card"
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="hero-content">
              <div className="hero-badge">
                <Activity size={15} />
                AI-POWERED CARE
              </div>

              <h2>Need a doctor?</h2>
              <h2>Just talk to us.</h2>

              <p>
                Our AI voice assistant can help you find doctors,
                check availability and book your appointments
                through a natural conversation.
              </p>

              <button className="hero-button" onClick={startCall}>
                <Phone size={17} />
                Start a voice call
                <ArrowUpRight size={17} />
              </button>

              <div className="hero-assurance">
                <ShieldCheck size={15} />
                Simple · Convenient · Always accessible
              </div>
            </div>

            <div className="hero-visual">
              <div className="hero-orbit orbit-one" />
              <div className="hero-orbit orbit-two" />

              <div className="hero-center-icon">
                <HeartPulse size={52} />
              </div>

              <div className="hero-floating-card floating-top">
                <div className="floating-icon">
                  <Phone size={17} />
                </div>
                <div>
                  <strong>Voice assistant</strong>
                  <span>Ready to help</span>
                </div>
              </div>

              <div className="hero-floating-card floating-bottom">
                <div className="floating-icon success">
                  <CheckCircle2 size={17} />
                </div>
                <div>
                  <strong>Easy appointments</strong>
                  <span>Book in a few steps</span>
                </div>
              </div>
            </div>
          </motion.section>

          {/* STATS */}
          <section className="stats-grid">
            <motion.div
              className="stat-card"
              whileHover={{ y: -3 }}
            >
              <div className="stat-icon doctors-stat">
                <Stethoscope size={20} />
              </div>
              <div className="stat-info">
                <span>Total doctors</span>
                <h3>{loadingDoctors ? "—" : doctors.length}</h3>
              </div>
            </motion.div>

            <motion.div
              className="stat-card"
              whileHover={{ y: -3 }}
            >
              <div className="stat-icon appointments-stat">
                <CalendarDays size={20} />
              </div>
              <div className="stat-info">
                <span>Appointments</span>
                <h3>
                  {loadingAppointments ? "—" : appointments.length}
                </h3>
              </div>
            </motion.div>

            <motion.div
              className="stat-card"
              whileHover={{ y: -3 }}
            >
              <div className="stat-icon slots-stat">
                <Clock size={20} />
              </div>
              <div className="stat-info">
                <span>Available slots</span>
                <h3>
                  {loadingDoctors
                    ? "—"
                    : doctors.reduce(
                        (total, doctor) =>
                          total + (doctor.available_slots?.length || 0),
                        0
                      )}
                </h3>
              </div>
            </motion.div>
          </section>

          {/* DOCTORS SECTION */}
          <section className="doctors-section" id="doctors">
            <div className="section-header">
              <div>
                <div className="section-eyebrow">
                  FIND YOUR SPECIALIST
                </div>
                <h3>Meet our doctors</h3>
                <p>Trusted care from experienced specialists.</p>
              </div>

              <button
                className="text-button"
                onClick={() => scrollToSection("doctors")}
              >
                View all doctors <ArrowUpRight size={16} />
              </button>
            </div>

            <div className="doctor-grid">
              {loadingDoctors ? (
                <p>Loading doctors...</p>
              ) : doctorError ? (
                <p className="error-message">{doctorError}</p>
              ) : doctors.length === 0 ? (
                <p>No doctors available.</p>
              ) : (
                doctors.map((doctor, index) => (
                  <motion.article
                    className="doctor-card"
                    key={doctor.id}
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    whileHover={{ y: -4 }}
                  >
                    <div className="doctor-card-top">
                      <div className="doctor-avatar">
                        {doctor.name
                          .split(" ")
                          .slice(-2)
                          .map((word) => word[0])
                          .join("")}
                      </div>

                      <span className="doctor-status">
                        <span />
                        Available
                      </span>
                    </div>

                    <h4>{doctor.name}</h4>

                    <span className="doctor-specialty">
                      {doctor.specialty}
                    </span>

                    <div className="doctor-detail">
                      <Users size={15} />
                      Medical specialist
                    </div>

                    <div className="doctor-detail">
                      <Clock size={15} />
                      {doctor.available_slots?.length || 0} slots available
                    </div>

                    <button
                      className="doctor-book-button"
                      onClick={startCall}
                    >
                      Book appointment <ArrowUpRight size={15} />
                    </button>
                  </motion.article>
                ))
              )}
            </div>
          </section>

          {/* APPOINTMENTS SECTION */}
          <section className="appointments-section" id="appointments">
            <div className="section-header">
              <div>
                <div className="section-eyebrow">
                  YOUR SCHEDULE
                </div>
                <h3>Appointments</h3>
                <p>Keep track of your upcoming appointments.</p>
              </div>

              <button
                className="text-button"
                onClick={loadAppointments}
              >
                Refresh <Activity size={16} />
              </button>
            </div>

            <div className="appointments-container">
              {loadingAppointments ? (
                <p>Loading appointments...</p>
              ) : appointmentError ? (
                <p className="error-message">{appointmentError}</p>
              ) : appointments.length === 0 ? (
                <div className="empty-appointments">
                  <div className="empty-icon">
                    <CalendarDays size={25} />
                  </div>
                  <h4>No appointments yet</h4>
                  <p>
                    Your booked appointments will appear here.
                    Start a voice call to book your first appointment.
                  </p>
                  <button
                    className="empty-book-button"
                    onClick={startCall}
                  >
                    <Phone size={16} />
                    Book an appointment
                  </button>
                </div>
              ) : (
                <div className="appointment-list">
                  {appointments.map((appointment) => (
                    <motion.div
                      className="appointment-card"
                      key={appointment.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                    >
                      <div className="appointment-doctor-icon">
                        <Stethoscope size={20} />
                      </div>

                      <div className="appointment-info">
                        <h4>{appointment.doctor_name}</h4>
                        <span>{appointment.specialty}</span>
                        <div className="appointment-patient">
                          Patient: {appointment.patient_name}
                        </div>
                      </div>

                      <div className="appointment-time">
                        <Clock size={15} />
                        {appointment.slot}
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </section>

          {/* FOOTER */}
          <footer className="dashboard-footer">
            <div>
              <HeartPulse size={17} />
              <span>MediVoice AI</span>
            </div>
            <p>Making healthcare more accessible, one conversation at a time.</p>
          </footer>
        </section>
      </main>

      {/* VOICE CALL MODAL */}
      <AnimatePresence>
        {isCallOpen && (
          <motion.div
            className="call-modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="call-modal"
              initial={{ opacity: 0, scale: 0.92, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.92, y: 20 }}
              transition={{ duration: 0.25 }}
            >
              <button
                className="call-close-button"
                onClick={endCall}
                aria-label="Close call window"
              >
                <X size={20} />
              </button>

              <div className="call-brand">
                <div className="call-brand-icon">
                  <HeartPulse size={21} />
                </div>
                <span>MediVoice AI</span>
              </div>

              <div className={`call-status-label status-${connectionStatus}`}>
  <span className="call-status-dot" />

  {connectionStatus === "connecting"
    ? "CONNECTING..."
    : connectionStatus === "connected"
    ? "CONNECTED"
    : connectionStatus === "error"
    ? "CONNECTION ERROR"
    : "DISCONNECTED"}
</div>

              <div className="call-avatar-container">
                <div className="call-avatar-ring ring-one" />
                <div className="call-avatar-ring ring-two" />
                <div className="call-avatar">
                  <HeartPulse size={42} />
                </div>
              </div>

              <h2>MediVoice Assistant</h2>
              <p className="call-subtitle">
                Your healthcare companion
              </p>

              <div className="call-timer">{formattedTime}</div>

              <div className="call-waveform">
  {Array.from({ length: 32 }).map((_, index) => {
    const heights = [12, 20, 32, 18, 42, 25, 14, 35, 22, 45, 16, 28];
    const height = heights[index % heights.length];

    return (
      <motion.span
        key={index}
        animate={{
          height: [`${height}px`, `${height + 15}px`, `${height}px`],
        }}
        transition={{
          duration: 0.8 + (index % 5) * 0.15,
          repeat: Infinity,
          repeatType: "reverse",
          delay: index * 0.03,
        }}
      />
    );
  })}
</div>

              <p className="call-message">
                Voice calling interface preview
              </p>

              <div className="call-security">
                <ShieldCheck size={15} />
                Your conversation is handled securely
              </div>

              <button
                className="end-call-button"
                onClick={endCall}
              >
                <Phone size={18} />
                End call
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
export default App;
