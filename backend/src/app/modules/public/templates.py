"""Default public legal page templates (platform scope, bn/en)."""

from __future__ import annotations

from typing import Final

LEGAL_DOCUMENT_KEYS: Final[dict[str, str]] = {
    "privacy": "public.privacy",
    "terms": "public.terms",
    "data-deletion": "public.data_deletion",
}

DEFAULT_PUBLIC_TEMPLATES: list[tuple[str, str, str, list[str]]] = [
    (
        "public.privacy",
        "en",
        "<h1>Privacy Policy</h1><p>We collect only data needed to operate your AI sales assistant. "
        "Messages and orders are stored per business (tenant) and are not used to train models for other "
        "businesses.</p><p>Contact your business administrator or platform support for data requests.</p>",
        [],
    ),
    (
        "public.privacy",
        "bn",
        "<h1>গোপনীয়তা নীতি</h1><p>আমরা শুধুমাত্র আপনার AI সেলস সহকারী পরিচালনার জন্য প্রয়োজনীয় "
        "তথ্য সংগ্রহ করি। বার্তা ও অর্ডার প্রতিটি ব্যবসার (টেন্যান্ট) আলাদা সংরক্ষিত হয় এবং অন্য "
        "ব্যবসার জন্য মডেল প্রশিক্ষণে ব্যবহার হয় না।</p>",
        [],
    ),
    (
        "public.terms",
        "en",
        "<h1>Terms of Service</h1><p>By using this platform you agree to lawful use, accurate business "
        "information, and compliance with messenger channel policies. Subscriptions and usage limits apply "
        "per your plan.</p>",
        [],
    ),
    (
        "public.terms",
        "bn",
        "<h1>সেবার শর্তাবলী</h1><p>এই প্ল্যাটফর্ম ব্যবহার করে আপনি আইনসম্মত ব্যবহার, সঠিক ব্যবসায়িক "
        "তথ্য এবং মেসেঞ্জার চ্যানেল নীতিমালা মেনে চলতে সম্মত হন।</p>",
        [],
    ),
    (
        "public.data_deletion",
        "en",
        "<h1>Data Deletion Instructions</h1><p>To request deletion of your customer conversation data, "
        "contact the business that messaged you. Business owners may request tenant data deletion from "
        "platform support with verified ownership.</p>",
        [],
    ),
    (
        "public.data_deletion",
        "bn",
        "<h1>তথ্য মুছে ফেলার নির্দেশনা</h1><p>গ্রাহক কথোপকথনের তথ্য মুছতে সংশ্লিষ্ট ব্যবসার সাথে যোগাযোগ করুন। "
        "ব্যবসার মালিকরা যাচাইকৃত মালিকানার পর প্ল্যাটফর্ম সাপোর্টে টেন্যান্ট ডেটা মুছে ফেলার অনুরোধ করতে পারেন।</p>",
        [],
    ),
]
