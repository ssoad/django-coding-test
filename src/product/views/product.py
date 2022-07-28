from django.views import generic

from product.models import Variant, Product

from product.models import ProductVariant

from product.models import ProductVariantPrice

from django.db.models import Q

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


class ListProductView(generic.TemplateView):
    template_name = 'products/list.html'

    def get_context_data(self, **kwargs):
        context = super(ListProductView, self).get_context_data(**kwargs)
        products = Product.objects.all()
        results = []
        for product in products:
            variants = ProductVariant.objects.filter(product=product, variant__active=True)

            vars_result = []
            for variant in variants:
                productvariantprice = ProductVariantPrice.objects.filter(Q(product_variant_one=variant) |
                                                                         Q(product_variant_two=variant)
                                                                         | Q(product_variant_three=variant)).first()
                if productvariantprice:
                    print(productvariantprice)
                    vars_result.append({'item': variant,
                                        'price': productvariantprice.price,
                                        'stock': productvariantprice.stock
                                        })
                else:
                    continue


            item = {'product': product,
                    'variants': vars_result,}
            results.append(item)
        page = self.request.GET.get('page', 1)

        paginator = Paginator(results, 5)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)
        context['results'] = results
        context['total_count'] = len(products)
        context['count'] = len(results)
        return context
