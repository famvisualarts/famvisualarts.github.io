# Boutique : mettre une œuvre en vente

1. **Stripe** (dashboard.stripe.com) → Liens de paiement → Créer :
   - Produit : titre de l'œuvre, photo, prix TTC en euros.
   - Cocher **Limiter le nombre de paiements** → 1 (le lien se désactive après la vente).
   - Cocher **Collecter l'adresse de livraison**, choisir les pays, ajouter les tarifs de livraison.
   - Après paiement → **Rediriger vers** `https://famvisualarts.github.io/shop/thanks/`.
   - Copier le lien `https://buy.stripe.com/...`.
2. Dans la fiche de l'œuvre (`_posts/gallery/....markdown`), ajouter dans l'en-tête :
   ```yaml
   price: 1200
   stripe_link: https://buy.stripe.com/xxxxxxxx
   ```
   Sans `stripe_link`, l'œuvre s'affiche avec son prix et un lien « Se renseigner ».
3. Après une vente : remplacer par `status: sold` (point rouge « Vendue »). `status: reserved` pour une réservation.
