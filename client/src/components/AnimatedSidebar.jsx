import React, { useState, createContext, useContext } from "react";
import { AnimatePresence, motion } from "motion/react";
import { IconMenu2, IconX } from "@tabler/icons-react";
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
    LayoutDashboard, 
    Briefcase, 
    Users, 
    FileText, 
    LogOut 
} from 'lucide-react';
import './AnimatedSidebar.css';

const SidebarContext = createContext(undefined);

export const useSidebar = () => {
    const context = useContext(SidebarContext);
    if (!context) {
        throw new Error("useSidebar must be used within a SidebarProvider");
    }
    return context;
};

export const SidebarProvider = ({
    children,
    open: openProp,
    setOpen: setOpenProp,
    animate = true
}) => {
    const [openState, setOpenState] = useState(false);
    const open = openProp !== undefined ? openProp : openState;
    const setOpen = setOpenProp !== undefined ? setOpenProp : setOpenState;

    return (
        <SidebarContext.Provider value={{ open, setOpen, animate: animate }}>
            {children}
        </SidebarContext.Provider>
    );
};

export const Sidebar = ({ children, open, setOpen, animate }) => {
    return (
        <SidebarProvider open={open} setOpen={setOpen} animate={animate}>
            {children}
        </SidebarProvider>
    );
};

export const SidebarBody = (props) => {
    return (
        <>
            <DesktopSidebar {...props} />
            <MobileSidebar {...props} />
        </>
    );
};

export const DesktopSidebar = ({ className, children, ...props }) => {
    const { open, setOpen, animate } = useSidebar();
    
    return (
        <motion.div
            className={`sidebar-desktop ${className || ''}`}
            style={{
                height: '100vh',
                padding: '1rem',
                display: 'flex',
                flexDirection: 'column',
                background: 'linear-gradient(180deg, #2563eb 0%, #1e40af 100%)',
                color: 'white',
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
                flexShrink: 0,
                position: 'sticky',
                top: 0,
            }}
            animate={{
                width: animate ? (open ? 300 : 80) : 300,
            }}
            transition={{
                duration: 0.3,
                ease: "easeInOut"
            }}
            onMouseEnter={() => setOpen(true)}
            onMouseLeave={() => setOpen(false)}
            {...props}
        >
            {children}
        </motion.div>
    );
};

export const MobileSidebar = ({ className, children, ...props }) => {
    const { open, setOpen } = useSidebar();
    
    return (
        <div
            className={`sidebar-mobile ${className || ''}`}
            style={{
                height: '64px',
                padding: '1rem',
                display: 'none',
                flexDirection: 'row',
                alignItems: 'center',
                justifyContent: 'space-between',
                width: '100%',
                background: 'linear-gradient(90deg, #2563eb 0%, #1e40af 100%)',
                color: 'white',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
            }}
            {...props}
        >
            <div style={{ display: 'flex', justifyContent: 'flex-end', zIndex: 20, width: '100%' }}>
                <IconMenu2
                    style={{ color: 'white', cursor: 'pointer' }}
                    onClick={() => setOpen(!open)}
                    size={28}
                />
            </div>
            <AnimatePresence>
                {open && (
                    <motion.div
                        initial={{ x: "-100%", opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        exit={{ x: "-100%", opacity: 0 }}
                        transition={{
                            duration: 0.3,
                            ease: "easeInOut",
                        }}
                        style={{
                            position: 'fixed',
                            height: '100%',
                            width: '100%',
                            inset: 0,
                            padding: '2.5rem',
                            zIndex: 100,
                            display: 'flex',
                            flexDirection: 'column',
                            justifyContent: 'space-between',
                            background: 'linear-gradient(180deg, #2563eb 0%, #1e40af 100%)',
                        }}
                    >
                        <div
                            style={{
                                position: 'absolute',
                                right: '2.5rem',
                                top: '2.5rem',
                                zIndex: 50,
                                color: 'white',
                                cursor: 'pointer'
                            }}
                            onClick={() => setOpen(!open)}
                        >
                            <IconX size={28} />
                        </div>
                        {children}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export const SidebarLink = ({ link, className, ...props }) => {
    const { open, animate } = useSidebar();
    const location = useLocation();
    const isActive = location.pathname === link.href;

    return (
        <Link
            to={link.href}
            className={`sidebar-link ${isActive ? 'sidebar-link-active' : ''} ${className || ''}`}
            style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'flex-start',
                gap: '0.75rem',
                padding: '0.75rem',
                borderRadius: '0.5rem',
                transition: 'all 0.2s',
                textDecoration: 'none',
                backgroundColor: isActive ? 'rgba(255, 255, 255, 0.2)' : 'transparent',
                color: isActive ? 'white' : 'rgba(191, 219, 254, 1)',
                fontWeight: isActive ? 600 : 400,
                boxShadow: isActive ? '0 4px 6px -1px rgba(0, 0, 0, 0.1)' : 'none',
            }}
            onMouseEnter={(e) => {
                if (!isActive) {
                    e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
                    e.currentTarget.style.color = 'white';
                }
            }}
            onMouseLeave={(e) => {
                if (!isActive) {
                    e.currentTarget.style.backgroundColor = 'transparent';
                    e.currentTarget.style.color = 'rgba(191, 219, 254, 1)';
                }
            }}
            {...props}
        >
            <div style={{ flexShrink: 0 }}>
                {link.icon}
            </div>
            <motion.span
                animate={{
                    display: animate ? (open ? "inline-block" : "none") : "inline-block",
                    opacity: animate ? (open ? 1 : 0) : 1,
                }}
                transition={{
                    duration: 0.2,
                    ease: "easeInOut"
                }}
                style={{
                    fontSize: '0.875rem',
                    whiteSpace: 'pre',
                    margin: 0,
                    padding: 0,
                }}
            >
                {link.label}
            </motion.span>
        </Link>
    );
};

// Main Sidebar Component with Navigation
const AnimatedSidebarComponent = () => {
    const navigate = useNavigate();
    const [sidebarOpen, setSidebarOpen] = useState(false);

    const handleLogout = () => {
        localStorage.removeItem('isAuthenticated');
        localStorage.removeItem('rememberMe');
        navigate('/login');
    };

    const navItems = [
        { 
            href: '/dashboard', 
            icon: <LayoutDashboard size={22} />, 
            label: 'Dashboard' 
        },
        { 
            href: '/dashboard/jobs', 
            icon: <Briefcase size={22} />, 
            label: 'Jobs' 
        },
        { 
            href: '/dashboard/candidates', 
            icon: <Users size={22} />, 
            label: 'Candidates' 
        },
        { 
            href: '/dashboard/assessments', 
            icon: <FileText size={22} />, 
            label: 'Assessments' 
        },
    ];

    return (
        <Sidebar animate={true} open={sidebarOpen} setOpen={setSidebarOpen}>
            <SidebarBody>
                <SidebarContent 
                    navItems={navItems} 
                    handleLogout={handleLogout}
                />
            </SidebarBody>
        </Sidebar>
    );
};

// Separate content component to use the sidebar context
const SidebarContent = ({ navItems, handleLogout }) => {
    const { open } = useSidebar();

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            {/* Logo Section */}
            <div style={{ marginBottom: '2rem' }}>
                <Link
                    to="/dashboard"
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.75rem',
                        padding: '0.75rem',
                        textDecoration: 'none',
                        color: 'white',
                    }}
                >
                    <div style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '50%',
                        background: 'rgba(255, 255, 255, 0.2)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                    }}>
                        <span style={{ fontWeight: 'bold', fontSize: '1.125rem' }}>M</span>
                    </div>
                    <motion.span
                        animate={{
                            display: open ? "inline-block" : "none",
                            opacity: open ? 1 : 0,
                        }}
                        transition={{ duration: 0.2 }}
                        style={{
                            fontSize: '1.125rem',
                            fontWeight: 700,
                            whiteSpace: 'nowrap',
                        }}
                    >
                        matrimony.com
                    </motion.span>
                </Link>
            </div>

            {/* Navigation Links */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: 1 }}>
                <motion.p 
                    animate={{
                        opacity: open ? 1 : 0,
                        display: open ? "block" : "none",
                    }}
                    transition={{ duration: 0.2 }}
                    style={{
                        color: 'rgba(191, 219, 254, 1)',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                        padding: '0 0.75rem',
                        marginBottom: '0.5rem',
                    }}
                >
                    Navigation
                </motion.p>
                {navItems.map((item, idx) => (
                    <SidebarLink key={idx} link={item} />
                ))}
            </div>

            {/* Logout Button */}
            <div style={{ 
                marginTop: 'auto', 
                paddingTop: '1rem', 
                borderTop: '1px solid rgba(255, 255, 255, 0.2)' 
            }}>
                <button
                    onClick={handleLogout}
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'flex-start',
                        gap: '0.75rem',
                        width: '100%',
                        padding: '0.75rem',
                        borderRadius: '0.5rem',
                        transition: 'all 0.2s',
                        backgroundColor: 'transparent',
                        color: 'rgba(191, 219, 254, 1)',
                        border: 'none',
                        cursor: 'pointer',
                        fontSize: '0.875rem',
                    }}
                    onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = 'rgba(239, 68, 68, 0.2)';
                        e.currentTarget.style.color = 'white';
                    }}
                    onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'transparent';
                        e.currentTarget.style.color = 'rgba(191, 219, 254, 1)';
                    }}
                >
                    <LogOut size={22} />
                    <motion.span
                        animate={{
                            display: open ? "inline-block" : "none",
                            opacity: open ? 1 : 0,
                        }}
                        transition={{ duration: 0.2 }}
                        style={{ whiteSpace: 'pre' }}
                    >
                        Logout
                    </motion.span>
                </button>
            </div>
        </div>
    );
};

export default AnimatedSidebarComponent;
