import { createApp, ref, computed, onMounted, watch } from 'vue';

createApp({
   setup() {
      /* --- State --- */
      const manifest = ref(null);
      const snapshot = ref(null);
      const loading = ref(true);
      const error = ref(null); // Robotustness: Error state
      const sidebarOpen = ref(false);
      const isMobile = ref(window.innerWidth <= 900);

      // Data Selection
      const activeCategoryCode = ref("");
      const availableDates = ref([]);
      const selectedDate = ref("");
      const selectedAuthor = ref("");
      // Search Debounce
      const searchParam = ref("");
      const searchQuery = ref("");
      let debounceTimer = null;

      watch(searchParam, (newVal) => {
         if (debounceTimer) clearTimeout(debounceTimer);
         debounceTimer = setTimeout(() => {
            searchQuery.value = newVal;
         }, 300); // 300ms debounce
      });

      // UX: Scroll Lock
      watch(sidebarOpen, (isOpen) => {
         if (isMobile.value) {
            document.body.style.overflow = isOpen ? 'hidden' : '';
         }
      });

      const expandedSet = ref(new Set());
      const authorsExpandedSet = ref(new Set()); // New: Authors Expansion

      const favorites = ref(JSON.parse(localStorage.getItem('my_favorites') || '[]'));
      const currentView = ref('papers'); // 'papers' | 'favorites' | 'trends';
      let chartInstance = null;

      // Theme
      const theme = ref(localStorage.getItem('theme') || 'dark');

      // Calendar State (UTC Fixed)
      const now = new Date();
      const todayStr = computed(() => now.toISOString().slice(0, 10)); // Local simplified

      const viewDate = ref(new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), 1)));

      /* --- Methods --- */

      // Fetch Helper (Smart Caching)
      const fetchJson = async (url) => {
         // Only add timestamp for manifest.json (mutable), allow caching for snapshots (immutable)
         const suffix = url.includes('manifest.json') ? '?t=' + Date.now() : '';
         const res = await fetch(url + suffix);
         if (!res.ok) throw new Error('Failed to load ' + url);
         return await res.json();
      };

      // Theme Logic
      const applyTheme = () => document.documentElement.setAttribute("data-theme", theme.value);
      const toggleTheme = () => {
         theme.value = theme.value === 'dark' ? 'light' : 'dark';
         localStorage.setItem('theme', theme.value);
         applyTheme();
      };
      applyTheme();

      // Calendar Logic
      const currentMonthLabel = computed(() => {
         return viewDate.value.toLocaleString('default', { year: 'numeric', month: 'long' });
      });

      const calendarDays = computed(() => {
         const year = viewDate.value.getUTCFullYear();
         const month = viewDate.value.getUTCMonth();

         const firstDayOfMonth = new Date(Date.UTC(year, month, 1));
         const lastDayOfMonth = new Date(Date.UTC(year, month + 1, 0));

         const days = [];

         // Padding days from prev month
         const startDay = firstDayOfMonth.getUTCDay(); // 0 is Sunday
         for (let i = 0; i < startDay; i++) {
            days.push({ dayNum: '', isCurrentMonth: false });
         }

         // Days of current month
         for (let d = 1; d <= lastDayOfMonth.getUTCDate(); d++) {
            const dateObj = new Date(Date.UTC(year, month, d));
            // Convert to YYYY-MM-DD
            const isoDate = dateObj.toISOString().slice(0, 10);

            days.push({
               dayNum: d,
               isCurrentMonth: true,
               dateStr: isoDate,
               hasData: availableDates.value.includes(isoDate)
            });
         }

         return days;
      });

      const changeMonth = (delta) => {
         const newDate = new Date(viewDate.value);
         newDate.setUTCMonth(newDate.getUTCMonth() + delta);
         viewDate.value = newDate;
      };

      const selectDate = async (date) => {
         if (selectedDate.value === date) return;
         selectedDate.value = date;
         // Auto-switch back to papers view if in favorites/trends
         if (currentView.value !== 'papers') switchView('papers');

         await loadSnapshot(date);
         if (isMobile.value) sidebarOpen.value = false;
      };

      const jumpToLatest = () => {
         if (availableDates.value.length) selectDate(availableDates.value[0]);
      };

      const latestDate = computed(() => availableDates.value[0] || '');

      // Data Loading
      const loadManifest = async () => {
         loading.value = true;
         error.value = null;
         try {
            const data = await fetchJson('./data/manifest.json');
            manifest.value = data;
            availableDates.value = data.dates || [];

            // Get URL params
            const params = new URLSearchParams(window.location.search);
            const qDate = params.get('date');
            const qCat = params.get('cat');

            // Robustness: Set Date logic updated
            if (qDate && availableDates.value.includes(qDate)) {
               selectedDate.value = qDate;
            } else if (availableDates.value.length) {
               selectedDate.value = availableDates.value[0]; // Default to latest
            }

            // Sync Calendar view to selected date (server time truth)
            if (selectedDate.value) {
               const parts = selectedDate.value.split('-');
               // Construct UTC date from string parts
               viewDate.value = new Date(Date.UTC(parseInt(parts[0]), parseInt(parts[1]) - 1, 1));
            }

            // Initial Load
            if (selectedDate.value) await loadSnapshot(selectedDate.value);

            // Set Category
            if (qCat) activeCategoryCode.value = qCat;

         } catch (e) {
            console.error(e);
            error.value = "无法加载数据。请检查网络连接或稍后重试。";
         } finally {
            loading.value = false;
         }
      };

      const loadSnapshot = async (date) => {
         loading.value = true;
         error.value = null;
         try {
            const data = await fetchJson(`./data/snapshots/${date}.json`);
            snapshot.value = data;

            // Determine active category
            if (!activeCategoryCode.value && data.categories.length) {
               activeCategoryCode.value = data.categories[0].code;
            } else {
               // Verify active category exists in new snapshot
               const exists = data.categories.find(c => c.code === activeCategoryCode.value);
               if (!exists && data.categories.length) {
                  activeCategoryCode.value = data.categories[0].code;
               }
            }

            // Update URL
            const url = new URL(window.location);
            url.searchParams.set('date', date);
            url.searchParams.set('cat', activeCategoryCode.value);
            window.history.replaceState({}, '', url);

         } catch (e) {
            console.error(e);
            error.value = `无法加载 ${date} 的数据。`;
         } finally {
            loading.value = false;
         }
      };

      const selectCategory = (code) => {
         activeCategoryCode.value = code;
         if (currentView.value !== 'papers') switchView('papers');

         window.scrollTo({ top: 0, behavior: 'smooth' });
         const url = new URL(window.location);
         url.searchParams.set('cat', code);
         window.history.replaceState({}, '', url);
         if (isMobile.value) sidebarOpen.value = false;
      };

      // Filtering
      const activeCategory = computed(() => {
         return snapshot.value?.categories?.find(c => c.code === activeCategoryCode.value);
      });

      // Pagination State
      const displayCount = ref(20);

      const filteredPapers = computed(() => {
         let papers = [];

         if (currentView.value === 'favorites') {
            papers = favorites.value;
         } else if (activeCategory.value) {
            papers = activeCategory.value.papers;
         } else {
            return [];
         }

         if (searchQuery.value) {
            const q = searchQuery.value.toLowerCase();
            papers = papers.filter(p =>
               p.title.toLowerCase().includes(q) ||
               p.authors.some(a => a.toLowerCase().includes(q))
            );
         }

         if (currentView.value !== 'favorites' && selectedAuthor.value) {
            papers = papers.filter(p => p.authors.includes(selectedAuthor.value));
         }

         return papers;
      });

      // Pagination Computed
      const visiblePapers = computed(() => {
         return filteredPapers.value.slice(0, displayCount.value);
      });

      const hasMorePapers = computed(() => {
         return visiblePapers.value.length < filteredPapers.value.length;
      });

      const loadMore = () => {
         displayCount.value += 20;
      };

      // Reset pagination when filters change
      watch([activeCategoryCode, searchQuery, selectedAuthor, selectedDate, currentView], () => {
         displayCount.value = 20;
         window.scrollTo({ top: 0, behavior: 'smooth' });
      });

      // Favorites Logic
      const isFavorite = (paper) => favorites.value.some(p => p.id === paper.id);

      const toggleFavorite = (paper) => {
         if (isFavorite(paper)) {
            favorites.value = favorites.value.filter(p => p.id !== paper.id);
         } else {
            favorites.value.unshift(paper); // Add to top
         }
         localStorage.setItem('my_favorites', JSON.stringify(favorites.value));
      };

      // View Switcher & Charts
      const switchView = (view) => {
         currentView.value = view;
         if (isMobile.value) sidebarOpen.value = false;

         if (view === 'trends') {
            setTimeout(initChart, 100);
         }
      };

      const initChart = () => {
         const ctx = document.getElementById('trendChart');
         if (!ctx || !manifest.value || !manifest.value.stats) return;

         if (chartInstance) chartInstance.destroy();

         const stats = [...manifest.value.stats].reverse(); // Sort by date asc
         const labels = stats.map(s => s.date);

         // Get all unique categories
         const catCodes = manifest.value.categories.map(c => c.code);

         // Prepare datasets
         const datasets = catCodes.map((code, idx) => {
            const colors = ['#f87171', '#60a5fa', '#34d399', '#facc15', '#a78bfa', '#fbbf24'];
            return {
               label: code,
               data: stats.map(s => s.counts[code] || 0),
               borderColor: colors[idx % colors.length],
               tension: 0.3,
               fill: false
            };
         });

         chartInstance = new Chart(ctx, {
            type: 'line',
            data: { labels, datasets },
            options: {
               responsive: true,
               maintainAspectRatio: false,
               color: '#9ca3af',
               plugins: {
                  legend: { labels: { color: '#e5e7eb' } }
               },
               scales: {
                  y: {
                     beginAtZero: true,
                     grid: { color: 'rgba(255,255,255,0.1)' },
                     ticks: { color: '#9ca3af' }
                  },
                  x: {
                     grid: { display: false },
                     ticks: { color: '#9ca3af', maxTicksLimit: 10 }
                  }
               }
            }
         });
      };

      // Helpers
      const isExpanded = (p) => expandedSet.value.has(p.id || p.url);
      const toggleExpanded = (p) => {
         const key = p.id || p.url;
         if (expandedSet.value.has(key)) expandedSet.value.delete(key);
         else expandedSet.value.add(key);
      };

      // New: Authors Expansion Helper
      const isAuthorsExpanded = (p) => authorsExpandedSet.value.has(p.id || p.url);
      const toggleAuthorsExpanded = (p) => {
         const key = p.id || p.url;
         if (authorsExpandedSet.value.has(key)) authorsExpandedSet.value.delete(key);
         else authorsExpandedSet.value.add(key);
      };

      // PDF Preview Logic
      const pdfPreviewUrl = ref(null);

      const openPdfPreview = (url) => {
         pdfPreviewUrl.value = url;
         document.body.style.overflow = 'hidden';
      };

      const closePdfPreview = () => {
         pdfPreviewUrl.value = null;
         document.body.style.overflow = '';
      };

      // Init
      onMounted(() => {
         window.addEventListener('resize', () => isMobile.value = window.innerWidth <= 900);
         loadManifest();

         // Infinite Scroll Observer
         const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting && hasMorePapers.value) {
               loadMore();
            }
         }, { rootMargin: '200px' });

         const sentinel = document.getElementById('scroll-sentinel');
         if (sentinel) observer.observe(sentinel);

         // Re-observe if sentinel is re-rendered (though Vue usually keeps the same root if v-if doesn't toggle parent)
         // For robustness in this simple setup, we'll watch filters to re-check sentinel presence if needed
         watch(hasMorePapers, (val, oldVal) => {
            if (val && !oldVal) {
               // If we have more papers again, make sure we are observing
               setTimeout(() => {
                  const el = document.getElementById('scroll-sentinel');
                  if (el) observer.observe(el);
               }, 100);
            }
         });
      });

      return {
         theme, toggleTheme,
         sidebarOpen, isMobile,
         loading, error, loadManifest,
         availableDates, selectedDate, latestDate,
         calendarDays, currentMonthLabel, changeMonth, selectDate, jumpToLatest, todayStr,
         snapshot, activeCategoryCode, selectCategory,
         searchParam, searchQuery, selectedAuthor,
         filteredPapers, visiblePapers, hasMorePapers, loadMore,
         isExpanded, toggleExpanded,
         currentView, switchView, isFavorite, toggleFavorite, favorites,
         isAuthorsExpanded, toggleAuthorsExpanded,
         pdfPreviewUrl, openPdfPreview, closePdfPreview // Export new methods
      };
   }
}).mount('#app');
