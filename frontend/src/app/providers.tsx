'use client';
import { ReactNode, useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';

const theme = createTheme({ palette: { mode: 'dark', primary: { main: '#2563eb' }, secondary: { main: '#0ea5e9' }, background: { default: '#0b1220', paper: '#17243a' }, text: { primary: '#f8fafc', secondary: '#94a3b8' }, error: { main: '#ef4444' }, warning: { main: '#f59e0b' }, success: { main: '#22c55e' } }, typography: { fontFamily: 'Inter, Arial, sans-serif', button: { textTransform: 'none', fontWeight: 700 } }, shape: { borderRadius: 6 }, components: { MuiTableCell: { styleOverrides: { root: { borderColor: '#334155', padding: '11px 12px' }, head: { color: '#94a3b8', fontSize: 10, fontWeight: 800, textTransform: 'uppercase', letterSpacing: .7 } } }, MuiButton: { defaultProps: { disableElevation: true } }, MuiTab: { styleOverrides: { root: { minHeight: 44, fontSize: 12, textTransform: 'none', fontWeight: 700 } } } } });

export function Providers({ children }: { children: ReactNode }) { const [client] = useState(() => new QueryClient()); return <QueryClientProvider client={client}><ThemeProvider theme={theme}><CssBaseline/>{children}</ThemeProvider></QueryClientProvider>; }
