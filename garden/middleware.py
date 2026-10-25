from .models import LANGUAGES
class SiteMiddleware:
    def __init__(self,get_response): self.get_response=get_response
    def __call__(self,request):
        lang=request.COOKIES.get('garden_language','en')
        request.garden_language = lang if lang in LANGUAGES else 'en'
        response=self.get_response(request)
        # Django admin uses inline styling; public pages use external assets only.
        style="'self' 'unsafe-inline'" if request.path.startswith('/admin/') else "'self'"
        response.headers['Content-Security-Policy']=f"default-src 'self'; script-src 'self'; style-src {style}; img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
        response.headers['Permissions-Policy']='camera=(), microphone=(), geolocation=()'
        if request.path.startswith(('/accounts/','/my-garden/','/admin/')):
            response.headers['Cache-Control']='private, no-store'
        return response
