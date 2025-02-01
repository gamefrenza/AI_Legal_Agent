import React, { useEffect, useState } from 'react';
import { Badge, Box, IconButton, Menu, MenuItem, Typography } from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';
import { useAuth } from '../contexts/AuthContext';

interface Notification {
    id: string;
    type: string;
    severity: string;
    message: string;
    details: any;
    timestamp: string;
    read: boolean;
}

const severityColors = {
    critical: '#d32f2f',
    high: '#f44336',
    medium: '#ff9800',
    low: '#4caf50'
};

const NotificationCenter: React.FC = () => {
    const { user } = useAuth();
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const [ws, setWs] = useState<WebSocket | null>(null);

    useEffect(() => {
        // Fetch initial unread notifications
        const fetchNotifications = async () => {
            try {
                const response = await fetch('/api/notifications/unread', {
                    headers: {
                        'Authorization': `Bearer ${user.token}`
                    }
                });
                const data = await response.json();
                setNotifications(data);
                setUnreadCount(data.filter((n: Notification) => !n.read).length);
            } catch (error) {
                console.error('Error fetching notifications:', error);
            }
        };

        fetchNotifications();

        // Set up WebSocket connection
        const wsConnection = new WebSocket(`ws://${window.location.host}/ws/notifications/${user.id}`);
        
        wsConnection.onmessage = (event) => {
            const notification: Notification = JSON.parse(event.data);
            setNotifications(prev => [notification, ...prev]);
            setUnreadCount(prev => prev + 1);
        };

        wsConnection.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        setWs(wsConnection);

        return () => {
            if (ws) {
                ws.close();
            }
        };
    }, [user]);

    const handleClick = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const handleNotificationClick = async (notification: Notification) => {
        if (!notification.read) {
            try {
                await fetch(`/api/notifications/${notification.id}/read`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${user.token}`
                    }
                });
                
                setNotifications(prev =>
                    prev.map(n =>
                        n.id === notification.id ? { ...n, read: true } : n
                    )
                );
                setUnreadCount(prev => prev - 1);
            } catch (error) {
                console.error('Error marking notification as read:', error);
            }
        }
        
        // Handle notification click based on type
        if (notification.type === 'compliance_issue') {
            // Navigate to document with compliance issues
            window.location.href = `/documents/${notification.details.document_id}`;
        }
        
        handleClose();
    };

    return (
        <Box>
            <IconButton
                color="inherit"
                onClick={handleClick}
                aria-label={`${unreadCount} unread notifications`}
            >
                <Badge badgeContent={unreadCount} color="error">
                    <NotificationsIcon />
                </Badge>
            </IconButton>
            
            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleClose}
                PaperProps={{
                    style: {
                        maxHeight: 400,
                        width: 360,
                    },
                }}
            >
                {notifications.length === 0 ? (
                    <MenuItem>
                        <Typography>No notifications</Typography>
                    </MenuItem>
                ) : (
                    notifications.map((notification) => (
                        <MenuItem
                            key={notification.id}
                            onClick={() => handleNotificationClick(notification)}
                            sx={{
                                backgroundColor: notification.read ? 'inherit' : 'action.hover',
                                borderLeft: `4px solid ${severityColors[notification.severity as keyof typeof severityColors]}`,
                            }}
                        >
                            <Box sx={{ width: '100%' }}>
                                <Typography variant="subtitle2" sx={{ fontWeight: notification.read ? 'normal' : 'bold' }}>
                                    {notification.message}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    {new Date(notification.timestamp).toLocaleString()}
                                </Typography>
                            </Box>
                        </MenuItem>
                    ))
                )}
            </Menu>
        </Box>
    );
};

export default NotificationCenter; 