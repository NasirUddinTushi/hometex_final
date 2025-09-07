# unfold_config.py
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "SITE_TITLE": "HomeTexIndustries Admin",
    "SITE_HEADER": "HomeTexIndustries",
    "SITE_URL": "/",
    "SITE_SYMBOL": "settings",  # top-left symbol

    # ===================== Sidebar Configuration =====================
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,   # ✅ ডুপ্লিকেট এড়াতে False করা হলো
        "navigation": [
            # Dashboard
            {
                "title": _("Dashboard"),
                "items": [
                    {"title": _("Home"), "icon": "dashboard", "link": reverse_lazy("admin:index")},
                ],
            },

            # Accounts
            {
                "title": _("Accounts"),
                "separator": True,
                "items": [
                    {
                        "title": _("Customers"),
                        "icon": "people",
                        "link": reverse_lazy("admin:accounts_customer_changelist"),
                    },
                    {
                        "title": _("Addresses"),
                        "icon": "location_on",
                        "link": reverse_lazy("admin:accounts_customeraddress_changelist"),
                    },
                ],
            },

            # Products Management
            {
                "title": _("Products Management"),
                "separator": True,
                "items": [
                    {
                        "title": _("Categories"),
                        "icon": "category",
                        "link": reverse_lazy("admin:products_category_changelist"),
                    },
                    {
                        "title": _("Products"),
                        "icon": "inventory_2",
                        "link": reverse_lazy("admin:products_product_changelist"),
                    },
                    {
                        "title": _("Product Images"),
                        "icon": "photo_library",
                        "link": reverse_lazy("admin:products_productimage_changelist"),
                    },
                    {
                        "title": _("Attributes"),
                        "icon": "tune",
                        "link": reverse_lazy("admin:products_attribute_changelist"),
                    },
                    {
                        "title": _("Attribute Values"),
                        "icon": "label",
                        "link": reverse_lazy("admin:products_attributevalue_changelist"),
                    },
                ],
            },

            # Orders Management
            {
                "title": _("Orders Management"),
                "separator": True,
                "items": [
                    {
                        "title": _("Orders"),
                        "icon": "shopping_cart_checkout",
                        "link": reverse_lazy("admin:orders_order_changelist"),
                    },
                    {
                        "title": _("Order Items"),
                        "icon": "format_list_bulleted",
                        "link": reverse_lazy("admin:orders_orderitem_changelist"),
                    },
                    {
                        "title": _("Discounts"),
                        "icon": "sell",
                        "link": reverse_lazy("admin:orders_discount_changelist"),
                    },
                ],
            },

            # Site Settings
            {
                "title": _("Site Settings"),
                "separator": True,
                "items": [
                    {
                        "title": _("Site Features"),
                        "icon": "widgets",
                        "link": reverse_lazy("admin:site_config_sitefeature_changelist"),
                    },
                    {
                        "title": _("Social Links"),
                        "icon": "link",
                        "link": reverse_lazy("admin:site_config_sociallink_changelist"),
                    },
                ],
            },

            # Content Management
            {
                "title": _("Content Management"),
                "separator": True,
                "items": [
                    {
                        "title": _("Testimonials"),
                        "icon": "reviews",
                        "link": reverse_lazy("admin:cms_testimonial_changelist"),
                    },
                    {
                        "title": _("Blog Authors"),
                        "icon": "person",
                        "link": reverse_lazy("admin:cms_blogauthor_changelist"),
                    },
                    {
                        "title": _("Blog Posts"),
                        "icon": "article",
                        "link": reverse_lazy("admin:cms_blogpost_changelist"),
                    },
                    {
                        "title": _("Info Pages"),
                        "icon": "description",
                        "link": reverse_lazy("admin:cms_infopage_changelist"),
                    },
                    {
                        "title": _("Home Sections"),
                        "icon": "view_quilt",
                        "link": reverse_lazy("admin:cms_homesection_changelist"),
                    },
                    {
                        "title": _("Contact Messages"),
                        "icon": "mail",
                        "link": reverse_lazy("admin:cms_contactmessage_changelist"),
                    },
                ],
            },
        ],
    },
}
