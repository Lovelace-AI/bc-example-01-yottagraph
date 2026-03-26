<template>
    <v-app class="theme-brand">
        <template v-if="showAppFramework">
            <AppHeader />

            <v-navigation-drawer permanent app width="200" color="transparent">
                <v-list nav density="compact" class="mt-2">
                    <v-list-item
                        v-for="item in navItems"
                        :key="item.to"
                        :title="item.title"
                        :prepend-icon="item.icon"
                        :to="item.to"
                        :active="isActive(item.to)"
                        rounded="lg"
                    />
                </v-list>
            </v-navigation-drawer>

            <v-main class="fill-height">
                <ServerStatus />
                <NuxtPage />
            </v-main>

            <v-dialog v-model="state.showSettingsDialog" max-width="600">
                <SettingsDialog />
            </v-dialog>

            <NotificationContainer />
            <ServerStatusFooter />
        </template>
        <template v-else>
            <NuxtPage />
        </template>
    </v-app>
</template>

<script setup lang="ts">
    import { state } from './utils/appState';

    const route = useRoute();
    const { userName } = useUserState();

    const noFrameworkRoutes = ['/login', '/a0callback', '/logout', '/pending'];

    const showAppFramework = computed(() => {
        if (noFrameworkRoutes.includes(route.path)) return false;
        if (!userName.value) return false;
        return true;
    });

    const navItems = [
        { title: 'Dashboard', icon: 'mdi-view-dashboard', to: '/' },
        { title: 'Apple', icon: 'mdi-apple', to: '/company/AAPL' },
        { title: 'Tesla', icon: 'mdi-car-electric', to: '/company/TSLA' },
        { title: 'Analyst', icon: 'mdi-robot', to: '/chat' },
    ];

    function isActive(to: string): boolean {
        if (to === '/') return route.path === '/';
        return route.path.startsWith(to);
    }
</script>
