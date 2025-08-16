// Global variables
let currentCustomerEmail = '';
let selectedRecommendation = null;
let isVoiceRecording = false;
let recognition = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    loadServices();
    setupEventListeners();
    initializeVoiceRecognition();
});

function initializeApp() {
    // Set minimum date for booking to today
    const bookingDateInput = document.getElementById('bookingDate');
    if (bookingDateInput) {
        const now = new Date();
        const localISOTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
        bookingDateInput.min = localISOTime;
    }
    
    // Initialize navigation
    setupNavigation();
}

function setupNavigation() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
        
        // Close menu when clicking on links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
            });
        });
    }
}

function setupEventListeners() {
    // Booking form submission
    const bookingForm = document.getElementById('bookingForm');
    if (bookingForm) {
        bookingForm.addEventListener('submit', handleBookingSubmission);
    }
    
    // Customer email input for AI recommendations
    const customerEmailInput = document.getElementById('customerEmail');
    if (customerEmailInput) {
        customerEmailInput.addEventListener('blur', loadAIRecommendations);
    }
    
    // Modal close events
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            closeAllModals();
        }
    });
    
    // Keyboard events
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAllModals();
        }
    });
}

// Modal Management
function openBookingModal() {
    document.getElementById('bookingModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeBookingModal() {
    document.getElementById('bookingModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    resetBookingForm();
}

function openCustomerPortal() {
    document.getElementById('customerPortalModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeCustomerPortal() {
    document.getElementById('customerPortalModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    resetCustomerPortal();
}

function openVoiceBooking() {
    document.getElementById('voiceModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeVoiceModal() {
    document.getElementById('voiceModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    stopVoiceRecording();
}

function closeAllModals() {
    closeBookingModal();
    closeCustomerPortal();
    closeVoiceModal();
}

// AI Recommendations
async function loadAIRecommendations() {
    const email = document.getElementById('customerEmail').value;
    if (!email || !email.includes('@')) return;
    
    currentCustomerEmail = email;
    
    try {
        const response = await fetch(`/recommendations/${email}`);
        const data = await response.json();
        
        if (data.success && data.recommendations.length > 0) {
            displayRecommendations(data.recommendations);
        }
    } catch (error) {
        console.error('Error loading recommendations:', error);
    }
}

function displayRecommendations(recommendations) {
    const section = document.getElementById('recommendationsSection');
    const grid = document.getElementById('recommendationsGrid');
    
    if (!section || !grid) return;
    
    grid.innerHTML = '';
    
    recommendations.forEach((rec, index) => {
        const card = createRecommendationCard(rec, index);
        grid.appendChild(card);
    });
    
    section.style.display = 'block';
}

function createRecommendationCard(recommendation, index) {
    const card = document.createElement('div');
    card.className = 'recommendation-card';
    card.onclick = () => selectRecommendation(recommendation, card);
    
    card.innerHTML = `
        <div class="rec-header">
            <span class="rec-title">${recommendation.service_name}</span>
            <span class="rec-price">$${recommendation.dynamic_price}</span>
        </div>
        <div class="rec-details">
            <span>${recommendation.category}</span>
            <span>${recommendation.duration_minutes} min</span>
        </div>
        <div class="rec-reasons">
            ${recommendation.reasons.join(' • ')}
        </div>
    `;
    
    return card;
}

function selectRecommendation(recommendation, cardElement) {
    // Remove previous selection
    document.querySelectorAll('.recommendation-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Select current card
    cardElement.classList.add('selected');
    selectedRecommendation = recommendation;
    
    // Update service select
    const serviceSelect = document.getElementById('serviceSelect');
    if (serviceSelect) {
        serviceSelect.value = recommendation.service_name;
    }
}

// Booking Submission
async function handleBookingSubmission(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const bookingData = {
        customer_name: formData.get('customerName'),
        customer_email: formData.get('customerEmail'),
        customer_phone: formData.get('customerPhone'),
        service_name: formData.get('serviceSelect'),
        booking_datetime: formData.get('bookingDate')
    };
    
    // Validate required fields
    if (!bookingData.customer_name || !bookingData.customer_email || 
        !bookingData.service_name || !bookingData.booking_datetime) {
        showNotification('Please fill in all required fields', 'error');
        return;
    }
    
    try {
        const response = await fetch('/book', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(bookingData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Booking confirmed successfully! 🎉', 'success');
            closeBookingModal();
            
            // Optional: Show booking confirmation details
            setTimeout(() => {
                showBookingConfirmation(result.booking_id, bookingData);
            }, 1000);
        } else {
            showNotification('Booking failed. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Booking error:', error);
        showNotification('Network error. Please check your connection.', 'error');
    }
}

function showBookingConfirmation(bookingId, bookingData) {
    const confirmationMessage = `
        🎉 Booking Confirmed!
        
        Service: ${bookingData.service_name}
        Date: ${new Date(bookingData.booking_datetime).toLocaleString()}
        Booking ID: ${bookingId}
        
        You'll receive a confirmation email shortly.
    `;
    
    alert(confirmationMessage);
}

// Customer Portal
async function loadCustomerPortal() {
    const email = document.getElementById('portalEmail').value;
    if (!email || !email.includes('@')) {
        showNotification('Please enter a valid email address', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/customer/${email}`);
        const data = await response.json();
        
        if (data.success) {
            displayCustomerData(data.customer);
        } else {
            showNotification('Customer not found. Please check your email or book an appointment first.', 'warning');
        }
    } catch (error) {
        console.error('Error loading customer data:', error);
        showNotification('Error loading customer data', 'error');
    }
}

function displayCustomerData(customer) {
    const loginSection = document.getElementById('portalLogin');
    const contentSection = document.getElementById('portalContent');
    
    if (!loginSection || !contentSection) return;
    
    loginSection.style.display = 'none';
    contentSection.style.display = 'block';
    
    contentSection.innerHTML = `
        <div class="customer-profile">
            <div class="profile-header">
                <h4>Welcome back, ${customer.name}! 👋</h4>
                <span class="tier-badge tier-${customer.tier.toLowerCase()}">${customer.tier} Member</span>
            </div>
            
            <div class="portal-stats">
                <div class="stat-card">
                    <div class="stat-value">${customer.loyalty_points}</div>
                    <div class="stat-label">Loyalty Points</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${customer.booking_history.length}</div>
                    <div class="stat-label">Total Bookings</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${customer.tier}</div>
                    <div class="stat-label">Membership Tier</div>
                </div>
            </div>
            
            <div class="booking-history">
                <h5>Recent Bookings</h5>
                ${customer.booking_history.length > 0 ? 
                    customer.booking_history.slice(0, 5).map(booking => `
                        <div class="booking-item">
                            <div class="booking-service">${booking.service_name}</div>
                            <div class="booking-date">${new Date(booking.booking_datetime).toLocaleDateString()}</div>
                            <div class="booking-price">$${booking.price}</div>
                            ${booking.rating ? `<div class="booking-rating">${'⭐'.repeat(booking.rating)}</div>` : ''}
                        </div>
                    `).join('') :
                    '<p>No bookings yet. <a href="#" onclick="closeCustomerPortal(); openBookingModal();">Book your first appointment!</a></p>'
                }
            </div>
            
            <div class="portal-actions">
                <button class="btn btn-primary" onclick="closeCustomerPortal(); openBookingModal();">
                    <i class="fas fa-plus"></i>
                    Book New Appointment
                </button>
                <button class="btn btn-secondary" onclick="loadAIRecommendations()">
                    <i class="fas fa-magic"></i>
                    Get AI Recommendations
                </button>
            </div>
        </div>
    `;
}

// Voice Recognition
function initializeVoiceRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onstart = function() {
            isVoiceRecording = true;
            updateVoiceStatus('🎤 Listening... Speak now!');
            document.getElementById('voiceBtn').innerHTML = '<i class="fas fa-stop"></i>Stop';
        };
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            displayVoiceTranscript(transcript);
            processVoiceCommand(transcript);
        };
        
        recognition.onerror = function(event) {
            console.error('Voice recognition error:', event.error);
            showNotification('Voice recognition error. Please try again.', 'error');
            stopVoiceRecording();
        };
        
        recognition.onend = function() {
            stopVoiceRecording();
        };
    } else {
        console.warn('Speech recognition not supported');
    }
}

function startVoiceBooking() {
    if (!recognition) {
        showNotification('Voice recognition not supported in your browser', 'error');
        return;
    }
    
    if (isVoiceRecording) {
        stopVoiceRecording();
    } else {
        recognition.start();
    }
}

function stopVoiceRecording() {
    if (recognition && isVoiceRecording) {
        recognition.stop();
    }
    
    isVoiceRecording = false;
    updateVoiceStatus('Click to start voice booking');
    document.getElementById('voiceBtn').innerHTML = '<i class="fas fa-microphone"></i>Start Recording';
}

function updateVoiceStatus(message) {
    const statusElement = document.getElementById('voiceStatus');
    if (statusElement) {
        statusElement.textContent = message;
    }
}

function displayVoiceTranscript(transcript) {
    const transcriptSection = document.getElementById('voiceTranscript');
    const transcriptText = document.getElementById('transcriptText');
    
    if (transcriptSection && transcriptText) {
        transcriptText.textContent = transcript;
        transcriptSection.style.display = 'block';
    }
}

function processVoiceCommand(transcript) {
    updateVoiceStatus('Processing your request...');
    
    // Simple voice command processing
    // In a real implementation, this would use NLP for better understanding
    
    const lowerTranscript = transcript.toLowerCase();
    
    // Extract service type
    const services = {
        'haircut': 'Classic Haircut',
        'facial': 'Deep Cleansing Facial',
        'massage': 'Full Body Massage',
        'manicure': 'Manicure',
        'pedicure': 'Pedicure',
        'coloring': 'Hair Coloring',
        'spa': 'Hair Spa Treatment'
    };
    
    let detectedService = null;
    for (const [keyword, serviceName] of Object.entries(services)) {
        if (lowerTranscript.includes(keyword)) {
            detectedService = serviceName;
            break;
        }
    }
    
    if (detectedService) {
        setTimeout(() => {
            updateVoiceStatus(`✅ Detected: ${detectedService}`);
            showNotification(`Great! I heard "${detectedService}". Redirecting to booking form...`, 'success');
            
            setTimeout(() => {
                closeVoiceModal();
                openBookingModal();
                
                // Pre-fill the service
                const serviceSelect = document.getElementById('serviceSelect');
                if (serviceSelect) {
                    serviceSelect.value = detectedService;
                }
            }, 2000);
        }, 1000);
    } else {
        setTimeout(() => {
            updateVoiceStatus('❌ Service not recognized. Please try again.');
            showNotification('Could not identify a service. Please try saying something like "Book a haircut"', 'warning');
        }, 1000);
    }
}

// Services Management
async function loadServices() {
    // Static services for now - in real app, this would fetch from API
    const services = [
        { name: 'Classic Haircut', category: 'Hair', price: 25, duration: 45, popularity: 0.8 },
        { name: 'Hair Coloring', category: 'Hair', price: 80, duration: 120, popularity: 0.7 },
        { name: 'Deep Cleansing Facial', category: 'Facial', price: 45, duration: 60, popularity: 0.9 },
        { name: 'Anti-Aging Facial', category: 'Facial', price: 70, duration: 75, popularity: 0.5 },
        { name: 'Manicure', category: 'Nails', price: 20, duration: 30, popularity: 0.8 },
        { name: 'Pedicure', category: 'Nails', price: 25, duration: 45, popularity: 0.7 },
        { name: 'Full Body Massage', category: 'Massage', price: 50, duration: 60, popularity: 0.6 },
        { name: 'Aromatherapy Massage', category: 'Massage', price: 65, duration: 75, popularity: 0.4 }
    ];
    
    displayServices(services);
}

function displayServices(services) {
    const grid = document.getElementById('servicesGrid');
    if (!grid) return;
    
    grid.innerHTML = services.map(service => `
        <div class="service-card">
            <div class="service-content">
                <div class="service-category">${service.category}</div>
                <h3 class="service-title">${service.name}</h3>
                <div class="service-price">$${service.price}</div>
                <div class="service-duration">${service.duration} minutes</div>
                <div class="service-actions" style="margin-top: 1rem;">
                    <button class="btn btn-primary" onclick="quickBook('${service.name}')">
                        <i class="fas fa-calendar-plus"></i>
                        Book Now
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function quickBook(serviceName) {
    openBookingModal();
    
    // Pre-select the service
    setTimeout(() => {
        const serviceSelect = document.getElementById('serviceSelect');
        if (serviceSelect) {
            serviceSelect.value = serviceName;
        }
    }, 100);
}

// Utility Functions
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    if (!notification) return;
    
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 4000);
}

function resetBookingForm() {
    const form = document.getElementById('bookingForm');
    if (form) {
        form.reset();
    }
    
    const recommendationsSection = document.getElementById('recommendationsSection');
    if (recommendationsSection) {
        recommendationsSection.style.display = 'none';
    }
    
    selectedRecommendation = null;
    currentCustomerEmail = '';
}

function resetCustomerPortal() {
    const loginSection = document.getElementById('portalLogin');
    const contentSection = document.getElementById('portalContent');
    
    if (loginSection) loginSection.style.display = 'block';
    if (contentSection) contentSection.style.display = 'none';
    
    const emailInput = document.getElementById('portalEmail');
    if (emailInput) emailInput.value = '';
}

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Progressive Web App functionality
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/sw.js')
            .then(function(registration) {
                console.log('SW registered: ', registration);
            })
            .catch(function(registrationError) {
                console.log('SW registration failed: ', registrationError);
            });
    });
}