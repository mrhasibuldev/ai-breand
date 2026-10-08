export type AccountId = string & { readonly __brand: 'AccountId' };
export type ResourceId = string & { readonly __brand: 'ResourceId' };

export type OwnershipScope = {
  readonly accountId: AccountId;
};

export function assertOwnership(scope: OwnershipScope, ownerAccountId: string): void {
  if (scope.accountId !== ownerAccountId) throw new Error('Ownership check failed');
}
