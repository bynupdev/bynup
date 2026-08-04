// Icon Library - Organized by categories
const IconLibrary = {
    categories: [
        {
            name: "E-commerce",
            slug: "ecommerce",
            icons: [
                { class: "fas fa-shopping-cart", name: "Shopping Cart", tags: ["cart", "shop", "buy"] },
                { class: "fas fa-shopping-bag", name: "Shopping Bag", tags: ["bag", "shop", "store"] },
                { class: "fas fa-shopping-basket", name: "Shopping Basket", tags: ["basket", "shop"] },
                { class: "fas fa-tag", name: "Tag", tags: ["price", "label", "sale"] },
                { class: "fas fa-tags", name: "Tags", tags: ["prices", "labels"] },
                { class: "fas fa-credit-card", name: "Credit Card", tags: ["payment", "card", "pay"] },
                { class: "fas fa-money-bill-wave", name: "Money", tags: ["cash", "payment", "dollar"] },
                { class: "fas fa-gift", name: "Gift", tags: ["present", "offer"] },
                { class: "fas fa-percent", name: "Percent", tags: ["discount", "sale", "offer"] },
                { class: "fas fa-truck", name: "Truck", tags: ["shipping", "delivery"] },
                { class: "fas fa-box", name: "Box", tags: ["package", "product"] },
                { class: "fas fa-box-open", name: "Box Open", tags: ["package", "unbox"] },
                { class: "fas fa-store", name: "Store", tags: ["shop", "market"] },
                { class: "fas fa-cash-register", name: "Cash Register", tags: ["checkout", "payment"] },
                { class: "fas fa-barcode", name: "Barcode", tags: ["scan", "product"] }
            ]
        },
        {
            name: "Social Media",
            slug: "social",
            icons: [
                { class: "fab fa-facebook", name: "Facebook", tags: ["social", "fb"] },
                { class: "fab fa-facebook-f", name: "Facebook F", tags: ["social", "fb"] },
                { class: "fab fa-facebook-messenger", name: "Messenger", tags: ["chat"] },
                { class: "fab fa-twitter", name: "Twitter", tags: ["social", "tweet"] },
                { class: "fab fa-instagram", name: "Instagram", tags: ["social", "ig"] },
                { class: "fab fa-linkedin", name: "LinkedIn", tags: ["professional", "business"] },
                { class: "fab fa-linkedin-in", name: "LinkedIn In", tags: ["professional"] },
                { class: "fab fa-youtube", name: "YouTube", tags: ["video", "play"] },
                { class: "fab fa-pinterest", name: "Pinterest", tags: ["pin"] },
                { class: "fab fa-pinterest-p", name: "Pinterest P", tags: ["pin"] },
                { class: "fab fa-tiktok", name: "TikTok", tags: ["video", "social"] },
                { class: "fab fa-snapchat", name: "Snapchat", tags: ["snap"] },
                { class: "fab fa-snapchat-ghost", name: "Snapchat Ghost", tags: ["snap"] },
                { class: "fab fa-whatsapp", name: "WhatsApp", tags: ["chat", "message"] },
                { class: "fab fa-telegram", name: "Telegram", tags: ["chat", "message"] },
                { class: "fab fa-discord", name: "Discord", tags: ["chat", "gaming"] },
                { class: "fab fa-reddit", name: "Reddit", tags: ["forum"] },
                { class: "fab fa-reddit-alien", name: "Reddit Alien", tags: ["forum"] }
            ]
        },
        {
            name: "Communication",
            slug: "communication",
            icons: [
                { class: "fas fa-envelope", name: "Envelope", tags: ["email", "mail", "message"] },
                { class: "fas fa-envelope-open", name: "Envelope Open", tags: ["email", "mail"] },
                { class: "fas fa-envelope-open-text", name: "Envelope Text", tags: ["email"] },
                { class: "fas fa-phone", name: "Phone", tags: ["call", "contact"] },
                { class: "fas fa-phone-alt", name: "Phone Alt", tags: ["call", "contact"] },
                { class: "fas fa-phone-volume", name: "Phone Volume", tags: ["call", "ring"] },
                { class: "fas fa-mobile-alt", name: "Mobile", tags: ["cell", "phone"] },
                { class: "fas fa-comment", name: "Comment", tags: ["chat", "message"] },
                { class: "fas fa-comments", name: "Comments", tags: ["chat", "messages"] },
                { class: "fas fa-comment-dots", name: "Comment Dots", tags: ["chat", "typing"] },
                { class: "fas fa-comment-alt", name: "Comment Alt", tags: ["chat"] },
                { class: "fas fa-comment-medical", name: "Medical Comment", tags: ["health"] },
                { class: "fas fa-sms", name: "SMS", tags: ["text", "message"] },
                { class: "fas fa-inbox", name: "Inbox", tags: ["email", "folder"] },
                { class: "fas fa-paper-plane", name: "Paper Plane", tags: ["send", "email"] },
                { class: "fas fa-share", name: "Share", tags: ["forward", "send"] },
                { class: "fas fa-share-alt", name: "Share Alt", tags: ["forward"] },
                { class: "fas fa-share-alt-square", name: "Share Square", tags: ["forward"] }
            ]
        },
        {
            name: "Arrows & Directions",
            slug: "arrows",
            icons: [
                { class: "fas fa-arrow-up", name: "Arrow Up", tags: ["up", "top"] },
                { class: "fas fa-arrow-down", name: "Arrow Down", tags: ["down", "bottom"] },
                { class: "fas fa-arrow-left", name: "Arrow Left", tags: ["left", "back"] },
                { class: "fas fa-arrow-right", name: "Arrow Right", tags: ["right", "next"] },
                { class: "fas fa-chevron-up", name: "Chevron Up", tags: ["up", "expand"] },
                { class: "fas fa-chevron-down", name: "Chevron Down", tags: ["down", "collapse"] },
                { class: "fas fa-chevron-left", name: "Chevron Left", tags: ["left", "back"] },
                { class: "fas fa-chevron-right", name: "Chevron Right", tags: ["right", "next"] },
                { class: "fas fa-angle-up", name: "Angle Up", tags: ["up", "small"] },
                { class: "fas fa-angle-down", name: "Angle Down", tags: ["down", "small"] },
                { class: "fas fa-angle-left", name: "Angle Left", tags: ["left", "small"] },
                { class: "fas fa-angle-right", name: "Angle Right", tags: ["right", "small"] },
                { class: "fas fa-caret-up", name: "Caret Up", tags: ["up", "menu"] },
                { class: "fas fa-caret-down", name: "Caret Down", tags: ["down", "menu"] },
                { class: "fas fa-caret-left", name: "Caret Left", tags: ["left", "menu"] },
                { class: "fas fa-caret-right", name: "Caret Right", tags: ["right", "menu"] },
                { class: "fas fa-long-arrow-alt-up", name: "Long Arrow Up", tags: ["up"] },
                { class: "fas fa-long-arrow-alt-down", name: "Long Arrow Down", tags: ["down"] },
                { class: "fas fa-long-arrow-alt-left", name: "Long Arrow Left", tags: ["left"] },
                { class: "fas fa-long-arrow-alt-right", name: "Long Arrow Right", tags: ["right"] },
                { class: "fas fa-arrows-alt", name: "Arrows Alt", tags: ["move", "expand"] },
                { class: "fas fa-arrows-alt-h", name: "Arrows Horizontal", tags: ["move", "width"] },
                { class: "fas fa-arrows-alt-v", name: "Arrows Vertical", tags: ["move", "height"] },
                { class: "fas fa-expand", name: "Expand", tags: ["fullscreen", "enlarge"] },
                { class: "fas fa-compress", name: "Compress", tags: ["fullscreen", "shrink"] },
                { class: "fas fa-expand-arrows-alt", name: "Expand Arrows", tags: ["fullscreen"] }
            ]
        },
        {
            name: "User Interface",
            slug: "ui",
            icons: [
                { class: "fas fa-home", name: "Home", tags: ["house", "main"] },
                { class: "fas fa-search", name: "Search", tags: ["find", "magnify"] },
                { class: "fas fa-user", name: "User", tags: ["profile", "person"] },
                { class: "fas fa-users", name: "Users", tags: ["group", "team"] },
                { class: "fas fa-user-circle", name: "User Circle", tags: ["profile", "avatar"] },
                { class: "fas fa-user-plus", name: "User Plus", tags: ["add", "signup"] },
                { class: "fas fa-user-minus", name: "User Minus", tags: ["remove"] },
                { class: "fas fa-user-check", name: "User Check", tags: ["verified"] },
                { class: "fas fa-user-lock", name: "User Lock", tags: ["secure", "private"] },
                { class: "fas fa-cog", name: "Cog", tags: ["settings", "gear"] },
                { class: "fas fa-cogs", name: "Cogs", tags: ["settings", "gears"] },
                { class: "fas fa-bell", name: "Bell", tags: ["notification", "alert"] },
                { class: "fas fa-bell-slash", name: "Bell Slash", tags: ["mute", "notification"] },
                { class: "fas fa-bookmark", name: "Bookmark", tags: ["save", "favorite"] },
                { class: "fas fa-bookmark", name: "Bookmark", tags: ["save", "favorite"] },
                { class: "fas fa-heart", name: "Heart", tags: ["like", "favorite"] },
                { class: "fas fa-star", name: "Star", tags: ["favorite", "rating"] },
                { class: "fas fa-star-half-alt", name: "Star Half", tags: ["rating"] },
                { class: "fas fa-thumbs-up", name: "Thumbs Up", tags: ["like", "approve"] },
                { class: "fas fa-thumbs-down", name: "Thumbs Down", tags: ["dislike", "reject"] },
                { class: "fas fa-check", name: "Check", tags: ["yes", "confirm"] },
                { class: "fas fa-check-circle", name: "Check Circle", tags: ["success", "complete"] },
                { class: "fas fa-check-square", name: "Check Square", tags: ["checkbox", "done"] },
                { class: "fas fa-times", name: "Times", tags: ["close", "no", "x"] },
                { class: "fas fa-times-circle", name: "Times Circle", tags: ["error", "close"] },
                { class: "fas fa-plus", name: "Plus", tags: ["add", "new"] },
                { class: "fas fa-plus-circle", name: "Plus Circle", tags: ["add", "new"] },
                { class: "fas fa-minus", name: "Minus", tags: ["subtract", "remove"] },
                { class: "fas fa-minus-circle", name: "Minus Circle", tags: ["remove"] },
                { class: "fas fa-info", name: "Info", tags: ["information"] },
                { class: "fas fa-info-circle", name: "Info Circle", tags: ["information"] },
                { class: "fas fa-question", name: "Question", tags: ["help", "support"] },
                { class: "fas fa-question-circle", name: "Question Circle", tags: ["help"] },
                { class: "fas fa-exclamation", name: "Exclamation", tags: ["warning", "alert"] },
                { class: "fas fa-exclamation-circle", name: "Exclamation Circle", tags: ["warning"] },
                { class: "fas fa-exclamation-triangle", name: "Warning", tags: ["alert", "danger"] },
                { class: "fas fa-fire", name: "Fire", tags: ["hot", "popular"] }
            ]
        },
        {
            name: "Business",
            slug: "business",
            icons: [
                { class: "fas fa-briefcase", name: "Briefcase", tags: ["work", "job"] },
                { class: "fas fa-chart-line", name: "Chart Line", tags: ["graph", "stats"] },
                { class: "fas fa-chart-bar", name: "Chart Bar", tags: ["graph", "stats"] },
                { class: "fas fa-chart-pie", name: "Chart Pie", tags: ["graph", "stats"] },
                { class: "fas fa-chart-area", name: "Chart Area", tags: ["graph"] },
                { class: "fas fa-calculator", name: "Calculator", tags: ["math", "finance"] },
                { class: "fas fa-file-invoice", name: "File Invoice", tags: ["bill", "receipt"] },
                { class: "fas fa-file-invoice-dollar", name: "Invoice Dollar", tags: ["bill"] },
                { class: "fas fa-file-signature", name: "File Signature", tags: ["contract"] },
                { class: "fas fa-file-contract", name: "File Contract", tags: ["agreement"] },
                { class: "fas fa-hand-holding-usd", name: "Hand Holding USD", tags: ["donation"] },
                { class: "fas fa-hand-holding-heart", name: "Hand Holding Heart", tags: ["charity"] },
                { class: "fas fa-chart-line", name: "Analytics", tags: ["stats", "data"] },
                { class: "fas fa-chart-pie", name: "Pie Chart", tags: ["stats"] },
                { class: "fas fa-clipboard-list", name: "Clipboard List", tags: ["checklist"] },
                { class: "fas fa-tasks", name: "Tasks", tags: ["todo", "list"] }
            ]
        },
        {
            name: "Media & Files",
            slug: "media",
            icons: [
                { class: "fas fa-camera", name: "Camera", tags: ["photo", "image"] },
                { class: "fas fa-camera-retro", name: "Camera Retro", tags: ["photo"] },
                { class: "fas fa-video", name: "Video", tags: ["camera", "movie"] },
                { class: "fas fa-film", name: "Film", tags: ["movie", "video"] },
                { class: "fas fa-image", name: "Image", tags: ["photo", "picture"] },
                { class: "fas fa-images", name: "Images", tags: ["photos", "gallery"] },
                { class: "fas fa-file", name: "File", tags: ["document"] },
                { class: "fas fa-file-alt", name: "File Alt", tags: ["document"] },
                { class: "fas fa-file-pdf", name: "File PDF", tags: ["document"] },
                { class: "fas fa-file-word", name: "File Word", tags: ["document"] },
                { class: "fas fa-file-excel", name: "File Excel", tags: ["spreadsheet"] },
                { class: "fas fa-file-powerpoint", name: "File PowerPoint", tags: ["presentation"] },
                { class: "fas fa-file-image", name: "File Image", tags: ["photo"] },
                { class: "fas fa-file-archive", name: "File Archive", tags: ["zip"] },
                { class: "fas fa-folder", name: "Folder", tags: ["directory"] },
                { class: "fas fa-folder-open", name: "Folder Open", tags: ["directory"] },
                { class: "fas fa-download", name: "Download", tags: ["save"] },
                { class: "fas fa-upload", name: "Upload", tags: ["share"] },
                { class: "fas fa-cloud", name: "Cloud", tags: ["storage"] },
                { class: "fas fa-cloud-upload-alt", name: "Cloud Upload", tags: ["upload"] },
                { class: "fas fa-cloud-download-alt", name: "Cloud Download", tags: ["download"] }
            ]
        },
        {
            name: "Forms & Input",
            slug: "forms",
            icons: [
                { class: "fas fa-edit", name: "Edit", tags: ["write", "pencil"] },
                { class: "fas fa-pencil-alt", name: "Pencil Alt", tags: ["edit", "write"] },
                { class: "fas fa-pen", name: "Pen", tags: ["edit"] },
                { class: "fas fa-pen-fancy", name: "Pen Fancy", tags: ["edit", "write"] },
                { class: "fas fa-pen-square", name: "Pen Square", tags: ["edit"] },
                { class: "fas fa-pen-nib", name: "Pen Nib", tags: ["design"] },
                { class: "fas fa-eraser", name: "Eraser", tags: ["delete", "remove"] },
                { class: "fas fa-trash", name: "Trash", tags: ["delete", "remove"] },
                { class: "fas fa-trash-alt", name: "Trash Alt", tags: ["delete"] },
                { class: "fas fa-trash-restore", name: "Trash Restore", tags: ["undo"] },
                { class: "fas fa-trash-restore-alt", name: "Trash Restore Alt", tags: ["undo"] },
                { class: "fas fa-check-double", name: "Check Double", tags: ["verify"] },
                { class: "fas fa-check-circle", name: "Check Circle", tags: ["success"] },
                { class: "fas fa-times-circle", name: "Times Circle", tags: ["error"] },
                { class: "fas fa-exclamation-circle", name: "Exclamation Circle", tags: ["warning"] },
                { class: "fas fa-exclamation-triangle", name: "Exclamation Triangle", tags: ["danger"] }
            ]
        },
        {
            name: "E-commerce",
            slug: "ecommerce",
            icons: [
                { class: "fas fa-shopping-cart", name: "Shopping Cart", tags: ["cart", "buy"] },
                { class: "fas fa-shopping-bag", name: "Shopping Bag", tags: ["bag", "store"] },
                { class: "fas fa-shopping-basket", name: "Shopping Basket", tags: ["basket"] },
                { class: "fas fa-credit-card", name: "Credit Card", tags: ["payment"] },
                { class: "fas fa-money-bill", name: "Money Bill", tags: ["cash"] },
                { class: "fas fa-money-bill-wave", name: "Money Bill Wave", tags: ["cash"] },
                { class: "fas fa-tag", name: "Tag", tags: ["price", "label"] },
                { class: "fas fa-tags", name: "Tags", tags: ["prices"] },
                { class: "fas fa-gift", name: "Gift", tags: ["present"] },
                { class: "fas fa-gift-card", name: "Gift Card", tags: ["present"] },
                { class: "fas fa-percent", name: "Percent", tags: ["sale", "discount"] },
                { class: "fas fa-truck", name: "Truck", tags: ["shipping", "delivery"] },
                { class: "fas fa-box", name: "Box", tags: ["package"] },
                { class: "fas fa-box-open", name: "Box Open", tags: ["package"] },
                { class: "fas fa-store", name: "Store", tags: ["shop"] },
                { class: "fas fa-store-alt", name: "Store Alt", tags: ["shop"] }
            ]
        },
        {
            name: "Food & Drink",
            slug: "food",
            icons: [
                { class: "fas fa-utensils", name: "Utensils", tags: ["food", "restaurant"] },
                { class: "fas fa-utensil-spoon", name: "Spoon", tags: ["utensil"] },
                { class: "fas fa-pizza-slice", name: "Pizza", tags: ["food"] },
                { class: "fas fa-hamburger", name: "Hamburger", tags: ["food", "burger"] },
                { class: "fas fa-cheese", name: "Cheese", tags: ["food"] },
                { class: "fas fa-bacon", name: "Bacon", tags: ["food"] },
                { class: "fas fa-egg", name: "Egg", tags: ["food"] },
                { class: "fas fa-coffee", name: "Coffee", tags: ["drink", "cafe"] },
                { class: "fas fa-mug-hot", name: "Mug Hot", tags: ["drink", "coffee"] },
                { class: "fas fa-tea", name: "Tea", tags: ["drink"] },
                { class: "fas fa-wine-glass", name: "Wine Glass", tags: ["drink", "alcohol"] },
                { class: "fas fa-wine-glass-alt", name: "Wine Glass Alt", tags: ["drink"] },
                { class: "fas fa-cocktail", name: "Cocktail", tags: ["drink"] },
                { class: "fas fa-beer", name: "Beer", tags: ["drink"] },
                { class: "fas fa-bottle-water", name: "Water Bottle", tags: ["drink"] }
            ]
        },
        {
            name: "Health & Fitness",
            slug: "health",
            icons: [
                { class: "fas fa-heartbeat", name: "Heartbeat", tags: ["health", "medical"] },
                { class: "fas fa-heart", name: "Heart", tags: ["love", "health"] },
                { class: "fas fa-heart-broken", name: "Heart Broken", tags: ["broken"] },
                { class: "fas fa-stethoscope", name: "Stethoscope", tags: ["doctor"] },
                { class: "fas fa-hospital", name: "Hospital", tags: ["medical"] },
                { class: "fas fa-hospital-alt", name: "Hospital Alt", tags: ["medical"] },
                { class: "fas fa-clinic-medical", name: "Clinic", tags: ["medical"] },
                { class: "fas fa-diagnoses", name: "Diagnoses", tags: ["medical"] },
                { class: "fas fa-pills", name: "Pills", tags: ["medicine"] },
                { class: "fas fa-capsules", name: "Capsules", tags: ["medicine"] },
                { class: "fas fa-syringe", name: "Syringe", tags: ["vaccine"] },
                { class: "fas fa-bolt", name: "Bolt", tags: ["energy", "lightning"] },
                { class: "fas fa-bicycle", name: "Bicycle", tags: ["exercise", "bike"] },
                { class: "fas fa-running", name: "Running", tags: ["exercise"] },
                { class: "fas fa-walking", name: "Walking", tags: ["exercise"] },
                { class: "fas fa-dumbbell", name: "Dumbbell", tags: ["gym", "weights"] }
            ]
        },
        {
            name: "Travel & Maps",
            slug: "travel",
            icons: [
                { class: "fas fa-map-marker-alt", name: "Map Marker", tags: ["location", "pin"] },
                { class: "fas fa-map", name: "Map", tags: ["location"] },
                { class: "fas fa-map-marked-alt", name: "Map Marked", tags: ["location"] },
                { class: "fas fa-map-signs", name: "Map Signs", tags: ["direction"] },
                { class: "fas fa-compass", name: "Compass", tags: ["direction"] },
                { class: "fas fa-location-arrow", name: "Location Arrow", tags: ["direction"] },
                { class: "fas fa-plane", name: "Plane", tags: ["flight", "airport"] },
                { class: "fas fa-plane-departure", name: "Plane Departure", tags: ["flight"] },
                { class: "fas fa-plane-arrival", name: "Plane Arrival", tags: ["flight"] },
                { class: "fas fa-train", name: "Train", tags: ["railway"] },
                { class: "fas fa-subway", name: "Subway", tags: ["metro"] },
                { class: "fas fa-bus", name: "Bus", tags: ["transport"] },
                { class: "fas fa-car", name: "Car", tags: ["auto", "vehicle"] },
                { class: "fas fa-taxi", name: "Taxi", tags: ["cab"] },
                { class: "fas fa-bicycle", name: "Bicycle", tags: ["bike"] },
                { class: "fas fa-hiking", name: "Hiking", tags: ["trail"] },
                { class: "fas fa-campground", name: "Campground", tags: ["camping"] }
            ]
        },
        {
            name: "Education",
            slug: "education",
            icons: [
                { class: "fas fa-graduation-cap", name: "Graduation Cap", tags: ["education", "school"] },
                { class: "fas fa-school", name: "School", tags: ["education"] },
                { class: "fas fa-book", name: "Book", tags: ["read", "education"] },
                { class: "fas fa-book-open", name: "Book Open", tags: ["read"] },
                { class: "fas fa-book-reader", name: "Book Reader", tags: ["read"] },
                { class: "fas fa-pencil-alt", name: "Pencil", tags: ["write"] },
                { class: "fas fa-pen", name: "Pen", tags: ["write"] },
                { class: "fas fa-ruler", name: "Ruler", tags: ["measure"] },
                { class: "fas fa-ruler-combined", name: "Ruler Combined", tags: ["measure"] },
                { class: "fas fa-calculator", name: "Calculator", tags: ["math"] },
                { class: "fas fa-flask", name: "Flask", tags: ["science", "lab"] },
                { class: "fas fa-microscope", name: "Microscope", tags: ["science"] },
                { class: "fas fa-atom", name: "Atom", tags: ["science"] },
                { class: "fas fa-brain", name: "Brain", tags: ["mind"] },
                { class: "fas fa-chalkboard", name: "Chalkboard", tags: ["teaching"] },
                { class: "fas fa-chalkboard-teacher", name: "Chalkboard Teacher", tags: ["teaching"] }
            ]
        },
        {
            name: "Weather",
            slug: "weather",
            icons: [
                { class: "fas fa-sun", name: "Sun", tags: ["weather", "day"] },
                { class: "fas fa-moon", name: "Moon", tags: ["night", "dark"] },
                { class: "fas fa-cloud", name: "Cloud", tags: ["weather"] },
                { class: "fas fa-cloud-sun", name: "Cloud Sun", tags: ["weather", "partly"] },
                { class: "fas fa-cloud-moon", name: "Cloud Moon", tags: ["weather", "night"] },
                { class: "fas fa-cloud-rain", name: "Cloud Rain", tags: ["weather", "rain"] },
                { class: "fas fa-cloud-sun-rain", name: "Cloud Sun Rain", tags: ["weather"] },
                { class: "fas fa-cloud-showers-heavy", name: "Heavy Rain", tags: ["weather"] },
                { class: "fas fa-cloud-hail", name: "Hail", tags: ["weather"] },
                { class: "fas fa-cloud-sleet", name: "Sleet", tags: ["weather"] },
                { class: "fas fa-cloud-snow", name: "Snow", tags: ["weather"] },
                { class: "fas fa-snowflake", name: "Snowflake", tags: ["winter", "snow"] },
                { class: "fas fa-wind", name: "Wind", tags: ["weather"] },
                { class: "fas fa-tornado", name: "Tornado", tags: ["weather"] },
                { class: "fas fa-temperature-high", name: "Temperature High", tags: ["hot"] },
                { class: "fas fa-temperature-low", name: "Temperature Low", tags: ["cold"] },
                { class: "fas fa-thermometer-half", name: "Thermometer", tags: ["temperature"] }
            ]
        }
    ],
    
    // Helper method to search icons
    searchIcons: function(query) {
        if (!query) return [];
        
        query = query.toLowerCase();
        const results = [];
        
        this.categories.forEach(category => {
            category.icons.forEach(icon => {
                if (icon.name.toLowerCase().includes(query) || 
                    icon.class.toLowerCase().includes(query) ||
                    icon.tags.some(tag => tag.toLowerCase().includes(query))) {
                    results.push({
                        ...icon,
                        category: category.name
                    });
                }
            });
        });
        
        return results;
    },
    
    // Get all icons
    getAllIcons: function() {
        const allIcons = [];
        this.categories.forEach(category => {
            category.icons.forEach(icon => {
                allIcons.push({
                    ...icon,
                    category: category.name
                });
            });
        });
        return allIcons;
    }
};

// Make it globally available
window.IconLibrary = IconLibrary;