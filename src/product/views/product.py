import datetime

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
        query_parms = self.request.GET

        context = super(ListProductView, self).get_context_data(**kwargs)
        query_title = query_parms.get('title')
        query_date = query_parms.get('date')

        #Product Title Query
        if query_title and query_date:
            date = datetime.datetime.strptime(query_date, '%Y-%m-%d').date()
            print(date)
            products = Product.objects.filter(title__icontains=query_title, created_at=date)
        if query_date:
            date = datetime.datetime.strptime(query_date, '%Y-%m-%d').date()
            print(date)
            products = Product.objects.filter(created_at=date)
        elif query_title:
            products = Product.objects.filter(title__icontains=query_title)
        else:
            products = Product.objects.all()

        results = []
        variant_ls = []
        variant_ls = ProductVariant.objects.values('variant_title').distinct()
        for product in products:
            query_variant = query_parms.get('variant')
            if query_variant:
                variants = ProductVariant.objects.filter(variant_title__icontains=query_variant)
            else:
                variants = ProductVariant.objects.filter(product=product, variant__active=True)

            vars_result = []
            query_price_from = query_parms.get('price_from')
            query_price_to = query_parms.get('price_to')
            for variant in variants:
                productvariantprice = ProductVariantPrice.objects.filter(Q(product_variant_one=variant) |
                                                                         Q(product_variant_two=variant)
                                                                         | Q(product_variant_three=variant)).first()

                if productvariantprice:
                    if query_price_from and query_price_to:
                        if productvariantprice.price>= float(query_price_from) and productvariantprice.price <=float(query_price_to):
                                vars_result.append({'item': variant,
                                            'price': productvariantprice.price,
                                            'stock': productvariantprice.stock
                                            })
                    else:
                        vars_result.append({'item': variant,
                                            'price': productvariantprice.price,
                                            'stock': productvariantprice.stock
                                            })
                else:
                    continue

            item = {'product': product,
                    'variants': vars_result, }
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
        context['variants_ls'] = variant_ls
        context['total_count'] = len(products)
        context['count'] = len(results)
        return context
