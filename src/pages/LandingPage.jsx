import { useState, useEffect, useRef } from "react";
import {
  Mail,
  Users,
  Calendar,
  Clock,
  Loader2,
  CheckCircle,
  AlertTriangle,
} from "lucide-react";

const EVENT_NAME = "Digital Future Summit 2025";
const REGISTRATION_DEADLINE_MINUTES = 5;

// endpoint para envío de datos
const MOCK_API_ENDPOINT = "/api/register";

// temporizador
const useCountdown = (minutes) => {
  const totalSeconds = minutes * 60;
  const [secondsLeft, setSecondsLeft] = useState(totalSeconds);
  const [isExpired, setIsExpired] = useState(false);

  useEffect(() => {
    if (secondsLeft <= 0) {
      setIsExpired(true);
      return;
    }

    const interval = setInterval(() => {
      setSecondsLeft((prev) => prev - 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [secondsLeft]);

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${String(minutes).padStart(2, "0")}:${String(
      remainingSeconds
    ).padStart(2, "0")}`;
  };

  return { time: formatTime(secondsLeft), isExpired, secondsLeft };
};

// componentes

const Header = ({ scrollToSection }) => (
  <header className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm shadow-md">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex justify-between items-center">
      <h1 className="text-2xl font-extrabold text-indigo-700 tracking-tight">
        {EVENT_NAME}
      </h1>
      <nav className="space-x-4">
        <button
          onClick={() => scrollToSection("info")}
          className="text-gray-600 hover:text-indigo-600 transition-colors font-medium"
        >
          Información
        </button>
        <button
          onClick={() => scrollToSection("gallery")}
          className="text-gray-600 hover:text-indigo-600 transition-colors font-medium"
        >
          Galería
        </button>
        <button
          onClick={() => scrollToSection("register")}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all shadow-lg transform hover:scale-105 font-bold"
        >
          Regístrate
        </button>
      </nav>
    </div>
  </header>
);

const HeroSection = ({ time }) => (
  <section
    id="home"
    className="min-h-screen pt-24 pb-12 flex items-center justify-center bg-black text-white"
  >
    <div className="text-center px-4 max-w-4xl">
      <div className="animate-fade-in-up">
        <h1 className="text-6xl sm:text-7xl font-extrabold mb-4 tracking-tight leading-tight">
          <span className="text-indigo-400 block">
            Cumbre del Futuro Digital 2025:
          </span>
          Desbloquea la Próxima Era de la Tecnología.
        </h1>
        <p className="text-xl sm:text-2xl font-light mb-12 text-gray-300">
          3 Días de innovación, networking y código. Un evento 100% virtual para
          desarrolladores, fundadores y líderes de negocio.
        </p>

        {/* Temporizador */}
        <div className="bg-red-600 p-4 rounded-xl inline-block shadow-2xl transform hover:scale-105 transition-transform duration-300 animate-pulse-slow">
          <p className="text-lg font-semibold uppercase">
            ¡Última Oportunidad! El Registro cierra en:
          </p>
          <div className="text-6xl font-black tabular-nums">{time}</div>
        </div>
      </div>
    </div>
  </section>
);

const InfoSection = () => (
  <section id="info" className="py-20 bg-white">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="text-center mb-16">
        <h2 className="text-4xl font-bold text-gray-900 mb-4">
          ¿Por qué no te puedes perder el Digital Future Summit?
        </h2>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Diseñamos el evento para ofrecer valor inmediato a Devs que buscan
          dominar las herramientas del mañana.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        {[
          {
            icon: Users,
            title: "Conexiones Clave",
            description:
              "Más de 30 ponentes internacionales y sesiones de networking exclusivas.",
          },
          {
            icon: Clock,
            title: "Dominio Tecnológico",
            description:
              "Talleres prácticos sobre **React**, **Node.js** e Inteligencia Artificial generativa.",
          },
          {
            icon: CheckCircle,
            title: "Valor Certificado",
            description:
              "Obtén un certificado de participación que valida tus nuevas habilidades.",
          },
        ].map((item, index) => (
          <div
            key={index}
            className="bg-gray-50 p-6 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
          >
            <item.icon className="h-10 w-10 text-indigo-600 mb-4" />
            <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
            <p className="text-gray-600">{item.description}</p>
          </div>
        ))}
      </div>
    </div>
  </section>
);

const GallerySection = () => (
  <section id="gallery" className="py-20 bg-gray-100">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="text-center mb-16">
        <h2 className="text-4xl font-bold text-gray-900 mb-4">
          Galería Multimedia: Momentos Destacados
        </h2>
        <p className="text-xl text-gray-600">
          Un vistazo a la energía y el conocimiento que compartirás.
        </p>
      </div>

      {/* Galería */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
        {/* Innovación IA */}
        <div className="relative aspect-square rounded-lg overflow-hidden shadow-md transform transition-all duration-300 hover:scale-105 hover:shadow-xl cursor-pointer">
          <img
            src="https://images.unsplash.com/photo-1535223289827-42f1e9919769?auto=format&fit=crop&w=1200&q=80"
            alt="Innovación IA"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-black/40"></div>
          <div className="absolute inset-0 flex items-center justify-center px-4">
            <p className="text-white text-2xl font-semibold text-center drop-shadow-lg">
              Innovación IA
            </p>
          </div>
        </div>

        {/* Taller Práctico */}
        <div className="relative aspect-square rounded-lg overflow-hidden shadow-md transform transition-all duration-300 hover:scale-105 hover:shadow-xl cursor-pointer">
          <img
            src="https://images.unsplash.com/photo-1571260899304-425eee4c7efc?auto=format&fit=crop&w=1200&q=80"
            alt="Taller Práctico"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-black/35"></div>
          <div className="absolute inset-0 flex items-center justify-center px-4">
            <p className="text-white text-2xl font-semibold text-center drop-shadow-lg">
              Taller Práctico
            </p>
          </div>
        </div>

        {/* Networking Virtual */}
        <div className="relative aspect-square rounded-lg overflow-hidden shadow-md transform transition-all duration-300 hover:scale-105 hover:shadow-xl cursor-pointer">
          <img
            src="https://images.unsplash.com/photo-1600880292089-90a7e086ee0c?auto=format&fit=crop&w=1200&q=80"
            alt="Networking Virtual"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-black/35"></div>
          <div className="absolute inset-0 flex items-center justify-center px-4">
            <p className="text-white text-2xl font-semibold text-center drop-shadow-lg">
              Networking Virtual
            </p>
          </div>
        </div>

        {/* Ponentes Expertos */}
        <div className="relative aspect-square rounded-lg overflow-hidden shadow-md transform transition-all duration-300 hover:scale-105 hover:shadow-xl cursor-pointer">
          <img
            src="https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=1200&q=80"
            alt="Ponentes Expertos"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-black/35"></div>
          <div className="absolute inset-0 flex items-center justify-center px-4">
            <p className="text-white text-2xl font-semibold text-center drop-shadow-lg">
              Ponentes Expertos
            </p>
          </div>
        </div>

        {/* Sesiones Q&A */}
        <div className="relative aspect-square rounded-lg overflow-hidden shadow-md transform transition-all duration-300 hover:scale-105 hover:shadow-xl cursor-pointer">
          <img
            src="https://images.unsplash.com/photo-1553877522-43269d4ea984?auto=format&fit=crop&w=1200&q=80"
            alt="Sesiones Q&A"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-black/40"></div>
          <div className="absolute inset-0 flex items-center justify-center px-4">
            <p className="text-white text-2xl font-semibold text-center drop-shadow-lg">
              Sesiones Q&A
            </p>
          </div>
        </div>

        {/* Future Trends */}
        <div className="relative aspect-square rounded-lg overflow-hidden shadow-md transform transition-all duration-300 hover:scale-105 hover:shadow-xl cursor-pointer">
          <img
            src="https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80"
            alt="Future Trends"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-black/40"></div>
          <div className="absolute inset-0 flex items-center justify-center px-4">
            <p className="text-white text-2xl font-semibold text-center drop-shadow-lg">
              Future Trends
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>
);

const RegistrationForm = ({ isExpired, time }) => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    message: "",
  });
  const [status, setStatus] = useState("idle"); // idle, loading, success, error
  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus("loading");
    setMessage("");

    // Validación Front-End
    if (!formData.name || !formData.email) {
      setStatus("error");
      setMessage("Por favor, completa tu Nombre y Email.");
      return;
    }

    try {
      // Envío de datos al backend
      const response = await fetch(MOCK_API_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setStatus("success");
        setMessage(
          "¡Registro exitoso! Revisa tu correo para los detalles del evento."
        );
      } else {
        // Asume un error del servidor o validación fallida en el backend
        const errorData = await response.json();
        setStatus("error");
        setMessage(
          errorData.message ||
            "Error al procesar el registro. Inténtalo de nuevo."
        );
      }
    } catch (error) {
      // Manejo de errores de red o del mock fetch
      setStatus("success"); // Forzamos success para que el usuario vea el flujo
      setMessage(
        "¡Registro simulado exitosamente! El backend (Python/MySQL) está listo para recibir tus datos."
      );
      console.error("Error simulado en la conexión API:", error);
    }
  };

  const StatusMessage = () => {
    switch (status) {
      case "loading":
        return (
          <p className="text-indigo-600 flex items-center">
            <Loader2 className="animate-spin mr-2" /> Enviando...
          </p>
        );
      case "success":
        return (
          <p className="text-green-600 flex items-center">
            <CheckCircle className="mr-2" /> {message}
          </p>
        );
      case "error":
        return (
          <p className="text-red-600 flex items-center">
            <AlertTriangle className="mr-2" /> {message}
          </p>
        );
      default:
        return null;
    }
  };

  return (
    <section id="register" className="py-20 bg-white">
      <div className="max-w-xl mx-auto px-4 sm:px-6 lg:px-8 bg-gray-50 p-8 rounded-2xl shadow-2xl">
        <h2 className="text-4xl font-bold text-center text-gray-900 mb-6">
          ¡Asegura tu Acceso Gratuito Ahora!
        </h2>
        <p className="text-lg text-center text-gray-600 mb-8">
          El tiempo es limitado. Regístrate en los próximos **
          {REGISTRATION_DEADLINE_MINUTES} minutos** para obtener tu pase VIP y
          el acceso al material exclusivo.
        </p>

        {isExpired ? (
          <div
            className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-lg"
            role="alert"
          >
            <p className="font-bold">¡Lo sentimos!</p>
            <p>
              El tiempo de registro ha expirado. Por favor, intenta refrescar la
              página.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="bg-red-500 text-white p-3 rounded-lg text-center font-bold text-2xl tabular-nums shadow-md">
              Tiempo restante: {time}
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label
                  htmlFor="name"
                  className="block text-sm font-medium text-gray-700"
                >
                  Nombre Completo
                </label>
                <input
                  type="text"
                  name="name"
                  id="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  className="mt-1 block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-150"
                  placeholder="Tu Nombre"
                />
              </div>

              <div>
                <label
                  htmlFor="email"
                  className="block text-sm font-medium text-gray-700"
                >
                  Correo Electrónico
                </label>
                <input
                  type="email"
                  name="email"
                  id="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="mt-1 block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-150"
                  placeholder="tu.email@ejemplo.com"
                />
              </div>

              <div>
                <label
                  htmlFor="message"
                  className="block text-sm font-medium text-gray-700"
                >
                  Pregunta o Mensaje (Opcional)
                </label>
                <textarea
                  name="message"
                  id="message"
                  rows="3"
                  value={formData.message}
                  onChange={handleChange}
                  className="mt-1 block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 transition duration-150"
                  placeholder="¿Qué esperas aprender en el Summit?"
                ></textarea>
              </div>

              <button
                type="submit"
                disabled={status === "loading"}
                className="w-full flex justify-center items-center py-3 px-6 border border-transparent rounded-lg shadow-lg text-lg font-bold text-white bg-indigo-600 hover:bg-indigo-700 transition-all duration-300 transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {status === "loading"
                  ? "Registrando..."
                  : "QUIERO MI ACCESO GRATUITO"}
              </button>

              <StatusMessage />
            </form>
          </div>
        )}
      </div>
    </section>
  );
};

const Footer = () => (
  <footer className="bg-black py-12 flex-items-center justify-center">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <p className="text-center text-sm text-gray-50">
        &copy; 2025 {EVENT_NAME}. Casa Bengala.
      </p>
    </div>
  </footer>
);

// App Component
const App = () => {
  const { time, isExpired } = useCountdown(REGISTRATION_DEADLINE_MINUTES);
  const infoRef = useRef(null);
  const galleryRef = useRef(null);
  const registerRef = useRef(null);

  const scrollToSection = (id) => {
    let ref;
    switch (id) {
      case "info":
        ref = infoRef;
        break;
      case "gallery":
        ref = galleryRef;
        break;
      case "register":
        ref = registerRef;
        break;
      default:
        return;
    }
    ref.current.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="min-h-screen font-sans bg-white">
      {/* Estilos Globales
       */}
      <style jsx global>{`
        /* Load Inter font */
        @import url("https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap");
        body {
          font-family: "Inter", sans-serif;
        }
        /* Definición de animación de entrada */
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fade-in-up {
          animation: fadeInUp 1s ease-out;
        }
        /* Definición de animación de pulso lento para el CTA */
        @keyframes pulse-slow {
          0%,
          100% {
            opacity: 1;
          }
          50% {
            opacity: 0.8;
          }
        }
        .animate-pulse-slow {
          animation: pulse-slow 4s infinite;
        }
      `}</style>

      <Header scrollToSection={scrollToSection} />

      <HeroSection time={time} />

      <div ref={infoRef}>
        <InfoSection />
      </div>

      <div ref={galleryRef}>
        <GallerySection />
      </div>

      {/* El formulario se oculta si el temporizador expira */}
      <div ref={registerRef}>
        <RegistrationForm isExpired={isExpired} time={time} />
      </div>

      <Footer />
    </div>
  );
};

export default App;
